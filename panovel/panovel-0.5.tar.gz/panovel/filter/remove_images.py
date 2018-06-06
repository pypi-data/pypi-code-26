from panflute import run_filter, Image


def remove_images(elem, doc):
    if isinstance(elem, Image):
        return []


if __name__ == "__main__":
    run_filter(remove_images)
