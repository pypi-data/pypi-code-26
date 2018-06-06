from panovel import run_pandoc_filter, CodeBlock


def check(self):
    return isinstance(self.elem, CodeBlock) and self.classes == self.tags


if __name__ == "__main__":
    run_pandoc_filter(["frontmatter"], '{text}', '{text}', '{text}', check=check)
