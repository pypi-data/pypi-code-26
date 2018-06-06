from panovel import run_pandoc_filter


if __name__ == "__main__":
    run_pandoc_filter(
        ["copyrights"],
        '\\begin{{copyrights}}\n{text}\n\\end{{copyrights}}\n',
        '\n<div class="copyrights">\n{text}\n</div>\n',
        '~~~\n{text}\n~~~\n')
