from panovel import run_pandoc_filter


if __name__ == "__main__":
    run_pandoc_filter(
        ["dedication"],
        '\\begin{{dedication}}\n{text}\n\\end{{dedication}}\n',
        '\n<div class="dedication">\n{text}\n</div>\n',
        '{text}\n')
