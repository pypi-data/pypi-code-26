from datetime import datetime
from pokrok.plugins import DefaultProgressMeterFactory, BaseProgressMeter
from pokrok.styles import Style, Widget, TextWidget


class LoggingProgressMeterFactory(DefaultProgressMeterFactory):
    def __init__(self):
        style_superset = Style([
            Widget.TEXT, Widget.COUNTER, Widget.ELAPSED, Widget.PERCENT
        ])
        super().__init__('logging', LoggingProgressMeter, style_superset)


class LoggingProgressMeter(BaseProgressMeter):
    """Progress meter that logs INFO messages at a specified interval.

    Args:
        interval: The reporting interval.
        mag_format: Function that formats an integer as a string with magnitude
            (e.g. 1000000 => 1M).
    """
    def __init__(
            self, mod, size, widgets, desc='', start=0, interval=1000,
            mag_format=None):
        super().__init__(size)
        self.logger = mod.getLogger()
        self.count = start or 0
        self.interval = interval
        self.mag_format = mag_format
        self.start_time = None

        message = []
        if desc:
            message.append(desc)
        for w in (widgets or [Widget.COUNTER]):
            if isinstance(w, TextWidget):
                message.append(w.text)
            elif w == Widget.COUNTER:
                if size:
                    if mag_format:
                        size_str = mag_format(size)
                    else:
                        size_str = str(size)
                    message.append('{count}/' + size_str)
                else:
                    message.append('{count}')
            elif w == Widget.PERCENT and size is not None:
                if Widget.COUNTER in widgets:
                    message.append('({percent:.0%})')
                else:
                    message.append('{percent:.0%}')
            elif w == Widget.ELAPSED:
                message.append('{elapsed:.1f} seconds')

        self.message = ' '.join(message)

    def start(self):
        super().start()
        self.start_time = datetime.now()

    def finish(self):
        super().finish()
        self.logger.info("Read a total of %s records", self.count)

    def increment(self, n=1):
        new_count = self.count + n
        if (new_count % self.interval) < (self.count % self.interval):
            if self.mag_format:
                count_str = self.mag_format(new_count)
            else:
                count_str = str(new_count)
            format_kwargs = dict(
                count=count_str,
                elapsed=datetime.now().timestamp() - self.start_time.timestamp()
            )
            if self.size:
                format_kwargs['percent'] = new_count / self.size
            self.logger.info(self.message.format(**format_kwargs))
        self.count = new_count
