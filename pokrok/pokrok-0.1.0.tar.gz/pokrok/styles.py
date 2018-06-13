import enum


class WidgetType(enum.Enum):
    BAR = 'BAR'
    ETA = 'ETA'
    ELAPSED = 'ELAPSED'
    SPINNER = 'SPINNER'
    COUNTER = 'COUNTER'
    PERCENT = 'PERCENT'
    TEXT = 'TEXT'


class WidgetMeta(type):
    _cache = {}

    def __getattr__(cls, key):
        if key not in WidgetMeta._cache:
            WidgetMeta._cache[key] = Widget(WidgetType[key])
        return WidgetMeta._cache[key]


class Widget(metaclass=WidgetMeta):
    def __init__(self, widget, config=None):
        self.widget_type = widget
        self.config = config

    def __eq__(self, other):
        if isinstance(other, WidgetType):
            return self.widget_type == other
        elif not isinstance(other, Widget):
            return False
        elif self.widget_type != other.widget_type:
            return False
        elif self.config is not None and other.config is not None:
            return self.config == other.config
        else:
            return True

    def __hash__(self):
        return hash(self.widget_type)

    def __repr__(self):
        return "Widget<type={}, config={}>".format(self.widget_type, self.config)


class TextWidget(Widget):
    def __init__(self, text):
        super().__init__(WidgetType.TEXT, config=dict(text=text))

    @property
    def text(self):
        return self.config['text']


class StyleManager(dict):
    def __init__(self, default_style=None):
        super().__init__()
        self['default'] = default_style or Style()

    def set_style_options(self, config, **kwargs):
        if 'styles' in config:
            for name, style_config in config['styles'].items():
                self[name] = Style(**style_config)
        if 'default_style' in config:
            if isinstance(config['default_style'], str):
                self['default'] = self[config['default_style']]
            else:
                self['default'] = Style(**config['default_style'])


class Style:
    """
    Args:
        widgets: Widgets to use for `sized` and `unsized` unless they are not
            None.
        sized: Widgets for sized progress meters.
        unsized: Widgets specifically for unsized progress meters.s
    """
    def __init__(self, widgets=None, sized=None, unsized=None):
        if widgets:
            self.sized = _resolve_widgets(sized or widgets)
            self.unsized = _resolve_widgets(unsized or widgets)
        else:
            self.sized = _resolve_widgets(sized)
            self.unsized = _resolve_widgets(unsized)

    def get_widgets(self, sized):
        return self.sized if sized else self.unsized


def _resolve_widgets(widgets):
    if widgets is None:
        return None
    return [
        Widget[w] if isinstance(w, str) else w
        for w in widgets
    ]
