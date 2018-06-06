from panflute import run_filter, RawBlock, RawInline


def remove_comments(elem, doc):
    if not isinstance(elem, RawBlock) and not isinstance(elem, RawInline):
        return

    if elem.format == "html" and elem.text[:4] == "<!--" and elem.text[-3:] == "-->":
        return []


if __name__ == "__main__":
    run_filter(remove_comments)
