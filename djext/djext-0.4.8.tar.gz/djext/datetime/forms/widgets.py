from django.forms import (
    DateInput as BaseDateInput,
    DateTimeInput as BaseDateTimeInput,
    TimeInput as BaseTimeInput,
    SplitDateTimeWidget as BaseSplitDateTimeWidget,
)


class DateInput(BaseDateInput):
    input_type = 'date'


class DateTimeInput(BaseDateTimeInput):
    input_type = 'datetime'


class DateTimeLocalInput(BaseDateTimeInput):
    input_type = 'datetime-local'


class TimeInput(BaseTimeInput):
    input_type = 'time'


class SplitDateTimeWidget(BaseSplitDateTimeWidget):
    """
    A widget that splits datetime input into two <input type="text"> boxes.
    """
    def __init__(self, attrs=None, date_format=None, time_format=None, date_attrs=None, time_attrs=None):
        widgets = (
            DateInput(
                attrs=attrs if date_attrs is None else date_attrs,
                format=date_format,
            ),
            TimeInput(
                attrs=attrs if time_attrs is None else time_attrs,
                format=time_format,
            ),
        )
        super().__init__(widgets)


class SplitHiddenDateTimeWidget(SplitDateTimeWidget):
    """
    A widget that splits datetime input into two <input type="hidden"> inputs.
    """
    template_name = 'django/forms/widgets/splithiddendatetime.html'

    def __init__(self, attrs=None, date_format=None, time_format=None, date_attrs=None, time_attrs=None):
        super().__init__(attrs, date_format, time_format, date_attrs, time_attrs)
        for widget in self.widgets:
            widget.input_type = 'hidden'
