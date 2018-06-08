"""
Dom Element
"""
import json
from typing import overload


from dome.utils import uncapitalize_name


class Node(list):
    def __init__(self, tag, *children, **attrs):
        super().__init__(children)
        self.tag = uncapitalize_name(tag)
        self.attrs = dict(attrs)

    def __call__(self, *children, **attrs):
        self.extend(children)
        self.attrs.update(attrs)
        return self

    def _dump_head(self):
        sb = [self.tag]
        for key, value in self.attrs.items():
            if value is not None:
                sb.append(' {}={}'.format(uncapitalize_name(key), json.dumps(value)))
        return ''.join(sb)

    def dumps(self):
        sb = []
        if len(self):
            sb.append('<{}>'.format(self._dump_head()))
            for child in self:
                if isinstance(child, str):
                    sb.append(child)
                else:
                    sb.append(child.dumps())
            sb.append('</{}>'.format(self.tag))
            return ''.join(sb)
        else:
            return '<{}/>'.format(self._dump_head())

    def jsfunc(self, *operands, funcname=''):
        return 'function {name}({args})'.format(
            name=funcname,
            args=','.join(operands),
        ) + '{return `' + self.dumps() + '`;}'


class Html(Node):
    @overload
    def __init__(self, *children, Xmlns=None, Id=None, Class=None, Title=None, Accesskey=None, **attrs): ...

    def __init__(self, *children, **attrs):
        super().__init__('html', *children, **attrs)

    def dumps(self):
        return '<!DOCTYPE html>\n' + super().dumps()


class Head(Node):
    def __init__(self, *children, **attrs):
        super().__init__('head', *children, **attrs)


class Body(Node):
    def __init__(self, *children, **attrs):
        super().__init__('body', *children, **attrs)


class Div(Node):
    @overload
    def __init__(self, *children, Id=None, Class=None, Title=None, Accesskey=None, **attrs): ...

    def __init__(self, *children, **attrs):
        super().__init__('div', *children, **attrs)


class Meta(Node):
    """https://www.w3schools.com/tags/tag_meta.asp"""
    @overload
    def __init__(self, *children, Charset=None, Content=None, HttpEquiv=None, Name=None,
                 Id=None, Class=None, Title=None, Accesskey=None, **attrs): ...

    def __init__(self, *children, **attrs):
        super().__init__('meta', *children, **attrs)


class Title(Node):
    @overload
    def __init__(self, *children, Id=None, Class=None, Title=None, Accesskey=None, **attrs): ...

    def __init__(self, *children, **attrs):
        super().__init__('title', *children, **attrs)


class Script(Node):
    """https://www.w3schools.com/tags/tag_script.asp"""
    @overload
    def __init__(self, *children, Async=None, Charset=None, Defer=None, Src=None, Type='text/javascript',
                 Id=None, Class=None, Title=None, Accesskey=None, **attrs): ...

    def __init__(self, *children, **attrs):
        if 'Type' not in attrs: attrs['Type'] = 'text/javascript'
        if not children:
            super().__init__('script', '', **attrs)
        else:
            super().__init__('script', *children, **attrs)


class Link(Node):
    """https://www.w3schools.com/tags/tag_link.asp"""
    @overload
    def __init__(self, *children, Crossorigin=None, Href=None, Hreflang=None, Media=None, Rel='stylesheet', Sizes=None, Type=None,
                 Id=None, Class=None, Title=None, Accesskey=None, **attrs): ...

    def __init__(self, *children, **attrs):
        if 'Rel' not in attrs: attrs['Rel'] = 'stylesheet'
        super().__init__('link', *children, **attrs)


class CssLink(Link):
    def __init__(self, Href):
        super().__init__(Href=Href, Rel='stylesheet', Type='text/css')


class Style(Node):
    @overload
    def __init__(self, *children, Media=None, Scoped=None, Type=None,
                 Id=None, Class=None, Title=None, Accesskey=None, **attrs): ...

    def __init__(self, *children, **attrs):
        super().__init__('style', *children, **attrs)


class A(Node):
    @overload
    def __init__(self, *children, Download=None, Href=None, Hreflang=None, Media=None, Rel=None, Target=None, Type=None,
                 Id=None, Class=None, Title=None, Accesskey=None, **attrs): ...

    def __init__(self, *children, **attrs):
        super().__init__('a', *children, **attrs)


class Em(Node):
    @overload
    def __init__(self, *children, Id=None, Class=None, Title=None, Accesskey=None, **attrs): ...

    def __init__(self, *children, **attrs):
        super().__init__('em', *children, **attrs)


class P(Node):
    @overload
    def __init__(self, *children, Id=None, Class=None, Title=None, Accesskey=None, **attrs): ...

    def __init__(self, *children, **attrs):
        super().__init__('p', *children, **attrs)


class H1(Node):
    @overload
    def __init__(self, *children, Id=None, Class=None, Title=None, Accesskey=None, **attrs): ...

    def __init__(self, *children, **attrs):
        super().__init__('h1', *children, **attrs)


class H2(Node):
    @overload
    def __init__(self, *children, Id=None, Class=None, Title=None, Accesskey=None, **attrs): ...

    def __init__(self, *children, **attrs):
        super().__init__('h2', *children, **attrs)


class H3(Node):
    @overload
    def __init__(self, *children, Id=None, Class=None, Title=None, Accesskey=None, **attrs): ...

    def __init__(self, *children, **attrs):
        super().__init__('h3', *children, **attrs)


class H4(Node):
    @overload
    def __init__(self, *children, Id=None, Class=None, Title=None, Accesskey=None, **attrs): ...

    def __init__(self, *children, **attrs):
        super().__init__('h4', *children, **attrs)


class H5(Node):
    @overload
    def __init__(self, *children, Id=None, Class=None, Title=None, Accesskey=None, **attrs): ...

    def __init__(self, *children, **attrs):
        super().__init__('h5', *children, **attrs)


class Label(Node):
    @overload
    def __init__(self, *children, For=None, Form=None, Id=None, Class=None, Title=None, Accesskey=None, **attrs): ...

    def __init__(self, *children, **attrs):
        super().__init__('label', *children, **attrs)


class Span(Node):
    @overload
    def __init__(self, *children, Id=None, Class=None, Title=None, Accesskey=None, **attrs): ...

    def __init__(self, *children, **attrs):
        super().__init__('span', *children, **attrs)
