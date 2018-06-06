from panovel import run_pandoc_filter


if __name__ == "__main__":
    run_pandoc_filter(
        ["noindent", "no-indent", "no_indent"],
        '\\noindent\n{text}\n',
        '<div class="noindent">\n{text}\n</div>\n')
