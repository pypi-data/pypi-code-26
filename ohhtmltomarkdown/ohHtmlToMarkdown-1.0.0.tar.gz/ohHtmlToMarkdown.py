import re
from bs4 import BeautifulSoup
from bs4.element import Tag, NavigableString, Comment

BLOCK_ELEMENTS__PARSED = ['section', 'div', 'html', 'body', 'head', 'article']

class Parser(object):
    FILE = 1
    STRING = 2

    def __init__(self, string, type=1):

        if type == 1:
            self.html = self.__readfile(string)
        else:
            self.html = string

        self.soup = BeautifulSoup(self.html, 'html.parser')
        self.fn = {}
        self.result = []
        self.__fn_dict_init()


    def __fn_dict_init(self):
        self.fn.update(h1 = self.__h)
        self.fn.update(h2 = self.__h)
        self.fn.update(h3 = self.__h)
        self.fn.update(h4 = self.__h)
        self.fn.update(h5 = self.__h)
        self.fn.update(h6 = self.__h)
        self.fn.update(p = self.__p)
        self.fn.update(a = self.__a)
        self.fn.update(img = self.__img)
        self.fn['del'] = self.__del
        self.fn.update(b = self.__b)
        self.fn.update(strong = self.__b)
        self.fn.update(i = self.__i)
        self.fn.update(em = self.__i)
        self.fn.update(hr = self.__hr)
        self.fn.update(br = self.__br)
        self.fn.update(ul = self.__ul)
        self.fn.update(ol = self.__ol)
        self.fn.update(table = self.__table)
        self.fn.update(blockquote = self.__blockquote)
        self.fn.update(code = self.__inline_code)
        self.fn.update(pre = self.__block_code)
        self.fn.update(span = self.__span)
        self.fn.update(title = self.__span)
        self.fn.update(time = self.__time)
        self.fn.update(iframe = self.__a)
        

        for x in BLOCK_ELEMENTS__PARSED:
            self.fn[x] = self.__block

    def convert(self):
        for t in self.soup.contents:
            if not isinstance(t, Tag):
                continue

            fn = self.fn.get(t.name)
            if not fn:
                continue
            
            self.result.append(fn(t))

        res = ''.join(self.result)
        res = self.__cleanup(res)
        return res

    def __cleanup(self, html_string):
        res = re.sub('[\\n]{3,}', '\n\n', html_string)
        return res

    def __readfile(self, string):
        with open(string, 'r', encoding='utf-8') as file:
            html = file.read()

        return html

    def __descendants_parser(self, tag):
        res = []
        for t in tag.contents:
            if isinstance(t, Tag):
                fn = self.fn.get(t.name)
                if not fn:
                    continue

                res.append(fn(t))

            # Must before NavigableString because
            # Comment is a subclass of it
            if isinstance(t, Comment):
                continue

            if isinstance(t, NavigableString):
                string = t.string.strip().replace('\n','')

                if string:
                    res.append(string)

        return ''.join(res)

    def __block(self, tag):
        ret = ''
        string = ''

        length = len(tuple(tag.descendants))

        if length == 1:
            t = tuple(tag.descendants)[0].name
            if self.fn.get(t):
                ret = self.fn.get(t)(tuple(tag.descendants)[0])
            else:
                ret = tag.string
        else:
            ret = self.__descendants_parser(tag)

        return ret.strip() if ret else ""

    def __a(self, tag):
        text = tag.text
        if text:
            text = text.strip()

        link = ''
        if tag.get('href'):
            link = tag.get('href')
        elif tag.get('src'):
            link = tag.get('src')

        res = "[{}]({})".format(text if text else 'link_without_label', link if link else '')
        return res

    def __h(self, tag):
        names = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']

        if tag.name not in names:
            return []

        res = '\n{} {}\n'.format('#' * int(tag.name[-1]), tag.text)
        return res

    def __p(self, tag):
        ret = ''
        string = ''

        length = len(tuple(tag.descendants))

        if length == 1:
            string = tag.string
        elif length == 2:
            ret += self.__special(tag)
        else:
            ret = self.__descendants_parser(tag)

        res = "\n\n{}\n{}\n".format(string, ret)
        return res

    def __img(self, tag):
        text = tag.text
        link = ''
        if tag.get('src'):
            link = tag.get('src')
        elif tag.get('data-original-src'):
            link = tag.get('data-original-src')

        res = "\n![{}]({})\n\n".format(text if text else 'image_without_label', link if link else '')
        return res

    def __del(self, tag):
        return "~~{}~~ ".format(tag.text)

    def __b(self, tag):
        string = ''

        length = len(tuple(tag.descendants))
        if length == 1:
            ret = tag.string
        elif length == 2:
            ret = self.__special(tag)
        else:
            ret = self.__descendants_parser(tag)

        if ret:
            ret = ret.strip()
            return "**{}** ".format(ret)
        else:
            return ""

    def __i(self, tag):
        return "*{}* ".format(tag.text)

    def __hr(self, tag):
        return "\n\n------\n\n"

    def __br(self, tag):
        return "\n"

    def __ul(self, tag):
        res = '\n'
        for li in tag.find_all('li'):
            if len(tuple(li.descendants)) > 1:
                tmp = self.__descendants_parser(li)
            else:
                tmp = li.text
            res += '- ' + tmp + '\n'

        res += '\n'
        return res

    def __ol(self, tag):
        res = '\n'
        cnt = 1
        for li in tag.find_all('li'):
            if len(tuple(li.descendants)) > 1:
                tmp = self.__descendants_parser(li)
            else:
                tmp = li.text
            res += str(cnt) + '. ' + tmp + '\n'
            cnt = cnt + 1

        res += '\n'
        return res


    def __table(self, tag):
        if not tag.thead or not tag.tbody:
           #print ("Detect a strang table structure. Either without thead or tbody.")
           return '```\n' + tag.text + '\n```'

        cols = 0
        ths = tag.thead.find_all('th')
        cols = len(ths)
        trs = tag.tbody.find_all('tr')

        # thead
        res = ''
        for th in ths:
            res += '| ' + th.text + ' '
        res += '|\n'

        for i in range(cols):
            res += '| -- '
        res += '|\n'

        # tbody
        for tr in trs:
            for td in tr.find_all('td'):
                res += '| ' + td.text + ' '
            res += '|\n'

        res = '\n' + res + '\n'
        return res

    def __blockquote(self, tag):
        return "> {}".format(tag.text)

    def __inline_code(self, tag):
        return "```" + tag.text + "```"

    def __block_code(self, tag):
        return "\n```\n" + tag.text + "\n```\n"

    def __span(self, tag):
        ret = ''
        string = ''

        length = len(tuple(tag.descendants))
        if length == 1:
            string = tag.string
        elif length == 2:
            ret = self.__special(tag)
        else:
            ret = self.__descendants_parser(tag)

        res = "{}\n{}".format(string, ret)

        return res

    def __time(self, tag):
        return tag.text.strip() + '\n'

    # to solve <p><i>a</i></p> issue
    # And I know it looks ridiculous
    def __special(self, tag):
        ret = ''
        t1 = tuple(tag.descendants)[0]
        if t1.name:
            ret += self.fn.get(t1.name)(tuple(tag.descendants)[0])
        else:
            ret += t1

        t2 = tuple(tag.descendants)[1]
        if t2 != t1.text:
            if t2.name:
                ret += self.fn.get(t2.name)(tuple(tag.descendants)[1])
            else:
                ret += t2

        return ret

def main():
    parser = Parser("<b>b</b>", Parser.STRING)
    ret = parser.convert()

    #with open("test/out.md", 'w', encoding='utf-8') as file:
    #    file.write(ret)


if __name__ == "__main__":
    main()