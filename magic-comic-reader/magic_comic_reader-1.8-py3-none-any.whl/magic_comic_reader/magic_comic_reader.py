import argparse
import os
import re
import sys
import traceback
import unicodedata
import urllib.request
import webbrowser
import zlib
from itertools import chain
from multiprocessing import Process, Pipe
from urllib.parse import urljoin
from urllib.request import pathname2url

from lxml import html

try:
    import tkinter as tk
    from tkinter import font, ttk, filedialog, messagebox
except ImportError:
    print('Error: tkinter is not installed.', file=sys.stderr)
    print("tkinter is supposed to be included with Python, but some Linux distributions don't include it by default. "
          "Please use your package manager to install tkinter. One of the following commands may help:",
          file=sys.stderr)
    print('sudo apt install python3-tk', file=sys.stderr)
    print('sudo dnf install python3-tkinter', file=sys.stderr)
    print('sudo yum install python3-tkinter', file=sys.stderr)
    print('sudo pacman -S tk', file=sys.stderr)
    sys.exit(1)

debugging = False


class Window(ttk.Frame):
    pad = 10

    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)
        parent.report_callback_exception = self.report_callback_exception
        self.parent = parent
        self.grid(row=0, column=0, sticky=tk.N + tk.S + tk.W + tk.E, padx=Window.pad, pady=Window.pad)
        self.parent.grid_rowconfigure(0, weight=1)
        self.parent.grid_columnconfigure(0, weight=1)
        parent.title('The Magic Comic Reader')
        parent.resizable(False, False)
        font_size = 13
        font.nametofont('TkDefaultFont').configure(size=font_size)
        font.nametofont('TkTextFont').configure(size=font_size)
        font.nametofont('TkFixedFont').configure(size=font_size)
        entry_width = 50

        self.label1 = ttk.Label(self, text='First Page URL:')
        self.entry1 = ttk.Entry(self, width=entry_width)
        self.label2 = ttk.Label(self, text='First Image URL:')
        self.entry2 = ttk.Entry(self, width=entry_width)
        self.label3 = ttk.Label(self, text='Second Page URL:')
        self.entry3 = ttk.Entry(self, width=entry_width)
        self.button = ttk.Button(self, text='Begin', command=self.begin)

        self.label1.grid(row=0, column=0, sticky=tk.W, padx=Window.pad, pady=Window.pad)
        self.entry1.grid(row=0, column=1, sticky=tk.W, padx=Window.pad, pady=Window.pad)
        self.label2.grid(row=1, column=0, sticky=tk.W, padx=Window.pad, pady=Window.pad)
        self.entry2.grid(row=1, column=1, sticky=tk.W, padx=Window.pad, pady=Window.pad)
        self.label3.grid(row=2, column=0, sticky=tk.W, padx=Window.pad, pady=Window.pad)
        self.entry3.grid(row=2, column=1, sticky=tk.W, padx=Window.pad, pady=Window.pad)
        self.button.grid(row=3, column=0, columnspan=2, sticky=tk.W + tk.E, padx=Window.pad, pady=Window.pad)

    def begin(self):
        self.parent.geometry(f'{self.parent.winfo_width()}x{self.parent.winfo_height()}')
        url1 = self.entry1.get().strip()
        url2 = self.entry2.get().strip()
        url3 = self.entry3.get().strip()
        for widget in self.winfo_children():
            widget.grid_forget()
            widget.destroy()
        self.grid_columnconfigure(0, weight=1)
        for i in range(3):
            self.grid_rowconfigure(i, weight=1)
        label = ttk.Label(self, text='Downloading...')
        label.grid(row=0, column=0, sticky=tk.W, padx=Window.pad, pady=Window.pad)
        self.stringVar = tk.StringVar()
        label = ttk.Label(self, textvariable=self.stringVar)
        label.grid(row=1, column=0, sticky=tk.W, padx=Window.pad, pady=Window.pad)
        progressbar = ttk.Progressbar(self, mode='indeterminate')
        progressbar.grid(row=2, column=0, sticky=tk.W + tk.E, padx=Window.pad, pady=Window.pad)
        progressbar.start()
        self.conn, child_conn = Pipe()
        self.process = Process(target=build_webpage, args=(child_conn, url1, url2, url3))
        self.process.daemon = True
        self.process.start()
        self.page_count = 0
        self.show_progress()

    def show_progress(self):
        message = None
        while self.conn.poll() and message != 'DONE' and message != 'ERROR':
            message = self.conn.recv()
            self.page_count += 1
        self.check_for_subprocess_error(message)
        if message == 'DONE':
            self.show_end_page()
        else:
            if message is not None:
                self.stringVar.set(f'Page {self.page_count}: {message}')
            self.after(30, self.show_progress)

    def show_end_page(self):
        for widget in self.winfo_children():
            widget.grid_forget()
            widget.destroy()
        label = ttk.Label(self, text='Done.')
        label.grid(row=0, column=0, sticky=tk.W, padx=Window.pad, pady=Window.pad)
        label = ttk.Label(self, text=f'Found {self.page_count - 1} pages.')
        label.grid(row=1, column=0, sticky=tk.W, padx=Window.pad, pady=Window.pad)
        button = ttk.Button(self, text='Save', command=self.save)
        button.grid(row=2, column=0, columnspan=2, sticky=tk.N + tk.S + tk.W + tk.E, padx=Window.pad, pady=Window.pad)

    def save(self):
        suggested_filename = self.conn.recv()
        self.check_for_subprocess_error(suggested_filename)
        output_file = filedialog.asksaveasfile(defaultextension='.html', filetypes=[('Webpage', '*.html')],
                                               initialfile=suggested_filename, parent=self.parent)
        if output_file is None:
            return
        output_filename = os.path.realpath(output_file.name)
        with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'reader.html')) as file:
            html_str = file.read()
        image_urls = self.conn.recv()
        self.check_for_subprocess_error(image_urls)
        html_str = html_str.replace('{{imageUrls}}', repr(image_urls))
        output_file.write(html_str)
        output_file.close()
        webbrowser.open('file:' + pathname2url(output_filename), new=2, autoraise=True)
        self.parent.destroy()

    def check_for_subprocess_error(self, message):
        if message == 'ERROR':
            self.show_error(self.conn.recv())
            self.parent.destroy()

    def report_callback_exception(self, *args):
        self.show_error(''.join(traceback.format_exception(*args)))

    def show_error(self, error_str):
        messagebox.showerror('Error', error_str)


class Nop:
    """Dummy class that does nothing."""

    def __init__(self, *args, **kwargs):
        pass

    def __call__(self, *args, **kwargs):
        return self

    def __getattr__(self, item):
        return self

    def __setattr__(self, key, value):
        return self


# Must be a top-level module function (?)
def build_webpage(conn, first_page_url, first_image_url, second_page_url):
    try:
        first_page = get_document(conn, first_page_url)
        image_urls = get_all_image_urls(conn, first_page, first_page_url, first_image_url, second_page_url)
        conn.send('DONE')
        conn.send(get_filename(first_page))
        conn.send(image_urls)
        conn.close()
    except:
        conn.send('ERROR')
        conn.send(''.join(traceback.format_exception(*sys.exc_info())))
        conn.close()


def get_all_image_urls(conn, first_page, first_page_url, first_image_url, second_page_url):
    image_paths = get_paths_to_url(first_page, first_page_url, first_image_url)
    next_page_paths = get_paths_to_url(first_page, first_page_url, second_page_url)
    page_urls = {first_page_url}
    image_urls = [first_image_url]
    url = second_page_url
    try:
        while True:
            page_urls.add(url)
            document = get_document(conn, url)
            try_for_each(image_paths, lambda image_path: image_urls.append(
                urljoin(url, document.xpath(image_path, smart_strings=False)[0].strip())))

            def get_next_page(next_page_path):
                new_url = urljoin(url, document.xpath(next_page_path, smart_strings=False)[0].strip())
                if new_url in page_urls:  # The last page may link to itself or a previous page.
                    raise ValueError(f'Already visited {new_url}')
                return new_url

            url = try_for_each(next_page_paths, get_next_page)
    except:
        # We will get some kind of exception after reaching the end of the comic.
        if debugging:
            traceback.print_exc()
    return image_urls


def try_for_each(iterable, callback):
    """
    For each item, pass it to the callback. Returns the callback's first successful return value. If the callback raises
    an error, it is ignored. If every item causes errors, the last received error is reraised. If the iterable is empty
    then the callback is not called and None is returned.
    """
    last_error = None
    for item in iterable:
        try:
            return callback(item)
        except BaseException as error:
            last_error = error
    if last_error is not None:
        raise last_error
    else:
        return None


def get_document(conn, url):
    conn.send(url)
    if debugging:
        print('Loading', url)
    request = urllib.request.Request(url)
    request.add_header('Accept',
                       'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8')
    request.add_header('Accept-Encoding', 'gzip, deflate')
    request.add_header('Accept-Language', 'en-US,en;q=0.9')
    request.add_header('Connection', 'close')
    request.add_header('Cookie', 'accepts=1; _sj_view_m=1; webcomic3_birthday_16ede78acc6fabfde8c31b1546b509cf=1')
    request.add_header('DNT', '1')
    request.add_header('Upgrade-Insecure-Requests', '1')
    request.add_header('User-Agent',
                       'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                       'Chrome/66.0.3359.181 Safari/537.36')
    with urllib.request.urlopen(request) as response:
        data = response.read()
        for encoding in reversed(response.info().get('Content-Encoding', failobj='').split(',')):
            data = decompress(data, encoding.strip())
    # print(data.decode('utf-8'))
    return html.document_fromstring(data)


def decompress(data, encoding):
    if encoding == 'gzip':
        return zlib.decompress(data, 16 + zlib.MAX_WBITS)
    elif encoding == 'deflate':
        try:
            return zlib.decompress(data)
        except zlib.error:
            return zlib.decompress(data, -zlib.MAX_WBITS)
    else:
        return data


def get_paths_to_url(document, base_url, target_url):
    """
    Searches the document for all instances of target_url and returns a list of xpaths. Raises ValueError if target_url
    is not found. Uses base_url to resolve relative urls. Includes permissive matches where URL fragments and queries
    are ignored. Permissive matches always follow the strict matches.
    """
    xpaths = [[], [], []]
    target_urls = (target_url, target_url.partition('#')[0], target_url.partition('?')[0].rstrip('/'))
    for element in document.xpath('//*'):
        for attrib_name, attrib_value in element.attrib.items():
            url = urljoin(base_url, attrib_value.strip())

            def xpath():
                return document.getroottree().getpath(element) + '/@' + attrib_name

            if url == target_urls[0]:
                xpaths[0].append(xpath())
            elif url.partition('#')[0] == target_urls[1]:
                xpaths[1].append(xpath())
            elif url.partition('?')[0].rstrip('/') == target_urls[2]:
                xpaths[2].append(xpath())
    if debugging:
        for i in range(len(xpaths)):
            print(f'Matches for "{target_urls[i]}":')
            print('  ' + '\n  '.join(xpaths[i]))
    xpaths = tuple(chain.from_iterable(xpaths))
    if xpaths:
        return xpaths
    else:
        raise ValueError(f"Link to '{target_url}' not found.")


def get_filename(document):
    default_name = 'The Magic Comic Reader'
    element = document.find('.//title')
    if element is None:
        return default_name
    value = unicodedata.normalize('NFKD', element.text)
    value = re.sub('[^\w\s-]', '', value)
    value = re.sub('[-\s]+', ' ', value).strip()[:30].strip()
    return value or default_name


def run_windowed():
    root = tk.Tk()
    Window(root)
    root.mainloop()


def run_console(first_page_url, first_image_url, second_page_url, output_filename):
    conn = Nop()
    first_page = get_document(conn, first_page_url)
    image_urls = get_all_image_urls(conn, first_page, first_page_url, first_image_url, second_page_url)
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'reader.html')) as file:
        html_str = file.read()
    html_str = html_str.replace('{{imageUrls}}', repr(image_urls))
    with open(output_filename, 'w') as file:
        file.write(html_str)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--console', nargs=4, metavar=('page1', 'image1', 'page2', 'file_out'),
                        help='Run in console mode given the first page URL, first image URL, second page URL, and the '
                             'full path for the output file including its name and extension.')
    args = parser.parse_args()
    if args.console:
        run_console(*args.console)
    else:
        run_windowed()


if __name__ == '__main__':
    main()
