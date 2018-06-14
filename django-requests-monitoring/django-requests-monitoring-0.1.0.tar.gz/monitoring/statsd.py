from datadog import DogStatsd


class StatsD:
    class __StatsD:
        def __init__(self, host, port, namespace):
            self.client = DogStatsd(host=host, port=port, namespace=namespace)
        def __str__(self):
            return repr(self) + self.client
    instance = None
    def __init__(self, host, port, namespace):
        if not StatsD.instance:
            StatsD.instance = StatsD.__StatsD(host, port, namespace)
        else:
            StatsD.instance.client = DogStatsd(host=host, port=port, namespace=namespace)
    def __getattr__(self, name):
        return getattr(self.instance, name)

