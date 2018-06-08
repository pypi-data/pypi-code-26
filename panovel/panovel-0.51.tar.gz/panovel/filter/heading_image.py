from panovel import run_pandoc_filter, Header


def check(self):
    return isinstance(self.elem, Header) \
           and self.elem.level <= int(self.get_metadata("heading-image-level", "2"))


def latex(self):
    return [self.elem,
            self.raw_block(f'\\includegraphics[width=\\textwidth]',
                           f'{{{self.get_metadata("heading-image")}}}')]


def html(self):
    self.classes.append("header_image")
    return [self.elem,
            self.raw_block(f'<div class="chapterdiv"><img alt="---" class="chapterimg" ',
                           f'src="{self.get_metadata("heading-image")}"/></div>')]


if __name__ == "__main__":
    run_pandoc_filter([], latex, html, check=check)
