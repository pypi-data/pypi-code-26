import re


def epub_process(original_text, fmt, cfg):
    if not cfg.get("frontmatter-heading"):
        return original_text
    new = re.sub(r'<h1>' + cfg["frontmatter-heading"] + '</h1>' +
                 r'.*?<div class="chapterdiv"><img alt="---" class="chapterimg" src=".*?" /></div>',
                 '', original_text, flags=re.DOTALL)
    return re.sub(r'<h1>' + cfg["frontmatter-heading"] + '</h1>', '', new)
