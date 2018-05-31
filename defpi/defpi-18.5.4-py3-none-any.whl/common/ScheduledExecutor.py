from threading import Timer


class ScheduledExecutor:
    # Drift of a couple of milliseconds per execution

    def __init__(self, interval, delay, function, *args, **kwargs):
        self._timer = None
        self.function = function
        self.interval = interval
        self.delay = delay
        self.args = args
        self.kwargs = kwargs
        self.isRunning = False
        self.first = True
        self.start()
        self.first = False

    def _run(self):
        self.isRunning = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.isRunning:
            self._timer = Timer(self.delay if self.first else self.interval, self._run)
            self._timer.start()
            self.isRunning = True

    def stop(self):
        self._timer.cancel()
        self.isRunning = False
