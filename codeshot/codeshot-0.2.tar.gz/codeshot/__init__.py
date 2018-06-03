import argparse
from codeshot.converter import get_width, get_height, make_html, to_png
from pygments import highlight
from pygments.formatters import HtmlFormatter, ImageFormatter
from pygments.lexers import PythonLexer

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--infile", help="code file to be converted to image", dest="infile")
    parser.add_argument("--outfile", help="output image filepath", dest="outfile")
    args = parser.parse_args()

    if args.infile is None:
        parser.error("--infile requires an argument")

    filepath = args.infile
    outfile = args.outfile if args.outfile is not None else "code.png"
    with open(filepath) as f:
        content = f.read()
        width = get_width(content)
        height = get_height(content)
        code_width = width*9 + 30
        code_height = height*20 + 50
        formatter = HtmlFormatter(nobackground=True, style="monokai")
        code_html = highlight(content, PythonLexer(), formatter)
        style_css = formatter.get_style_defs('.highlight')
        html_filepath = make_html(style_css, code_html, code_width, code_height)
        to_png(html_filepath, code_width, code_height, outfile)

