import re


def transform(original_text, fmt, cfg, _):
    style = "default"
    if cfg.get("new-scene-style"):
        style = cfg.get("new-scene-style", "default")

    def style_new_scene(_):
        if fmt == "latex" or fmt == "pdf":
            if style == "text":
                return ''.join([r"\begin{center}", cfg.get("new-scene-text", "* * *"), r"\end{center}",
                                '\n', r"\noindent", "\n"])
            elif style == "fleuron":
                return ''.join([r"\begin{center}", '\n',
                                r"\includegraphics[width=0.1", r"\textwidth]",
                                f'{{{cfg.get("new-scene-image")}}}',
                                "\n", r"\end{center}", '\n', r"\noindent", "\n"])
            return ''.join([r"\par", "\n", r"\vspace{\baselineskip}", "\n",
                            r"\par", "\n\n" + r"\noindent" + "\n"])
        elif fmt == "html" or fmt == "epub" or fmt == "epub3":
            if style == "text":
                text = re.sub(r"([^\w])", r"\\\1", cfg.get("new-scene-text", "* * *"))
                return f'<p class="NewScene">{text}</p>'
            elif style == "fleuron":
                return '<div class="NewScene"><img alt="***" class="szeneimg" '\
                       f'src="{cfg.get("new-scene-image")}" /></div>'
            return '<p class="NewScene"> </p>'
        return "\n                            * * *\n"

    return re.sub(r'(^\s*\*\s*\*\s*\*\s*\n)', style_new_scene, original_text, flags=re.MULTILINE)
