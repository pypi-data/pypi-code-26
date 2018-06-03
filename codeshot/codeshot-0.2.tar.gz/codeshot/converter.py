import os
import sys
from selenium import webdriver

def get_width(content):
    lines = content.split("\n")
    max_width = 0
    for line in lines:
        width = len(line)
        if width > max_width:
            max_width = width
    return max_width

def get_height(content):
    lines = content.split("\n")
    max_height = len(lines)
    return max_height

def to_png(html_filepath, code_width, code_height, outfile):
    folder = os.path.dirname(__file__)
    outpath = os.path.join(folder, outfile)
    driver = webdriver.PhantomJS(service_log_path='/tmp/ghostdriver.log')
    driver.set_window_size(code_width+60, code_height)
    driver.get(html_filepath)
    driver.save_screenshot(outpath)
    driver.quit()
    os.remove(html_filepath)

def make_html(style_css, code_html, code_width, code_height):
    css = "\
    .rcorner {{ \
        border-radius: 15px; \
        background: #272822; \
        width: {}px; \
        height: {}px; \
        box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0 rgba(0, 0, 0, 0.19); \
        font-size: 14px; \
        padding: 20px; \
    }} \
    .rcorner .highlight {{ \
    }}".format(code_width, code_height)
    result_css = style_css + css
    html = "<!DOCTYPE html><html><head><style>{}</style></head><body><div class=\"rcorner\">{}</div></body></html>".format(result_css, code_html)
    folder = os.path.dirname(__file__)
    outpath = os.path.join(folder, "out.html")
    with open(outpath, "w") as f:
        f.write(html)
    return outpath
