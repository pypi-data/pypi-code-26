def with_headers(config_str, template_class):
    headers = _build_headers(template_class=template_class)
    return headers + "\n\n" + config_str


def _build_headers(template_class):
    header_template = "#ngrp:{header} {value}"
    headers = [
        ("version", 1),
        ("template", template_class.__name__),
    ]
    headers_str = "\n".join(
        header_template.format(header=header, value=value)
        for header, value in headers)
    return headers_str
