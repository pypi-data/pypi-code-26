from applauncher.kernel import Configuration, KernelReadyEvent, KernelShutdownEvent
import inject
import logging
from apscheduler.schedulers.background import BackgroundScheduler


class Scheduler(object):
    pass


class APSchedulerBundle(object):

    def __init__(self):

        self.config_mapping = {
            "apscheduler": {
                "jobstores": "",
                "executors": "",
                "coalesce": False,
                "max_instances": 3,
                "timezone": "UTC"
            }
        }

        self.scheduler = BackgroundScheduler()

        self.injection_bindings = {
            Scheduler: self.scheduler
        }

        self.event_listeners = [
            (KernelReadyEvent, self.kernel_ready),
            (KernelShutdownEvent, self.kernel_shutdown)
        ]

    def kernel_shutdown(self, event):
        self.scheduler.shutdown()

    @inject.params(config=Configuration)
    def kernel_ready(self, event, config):
        self.scheduler.configure(self.build_config(config.apscheduler))
        self.scheduler.start()
        logging.info("APScheduler ready")

    def build_config(self, config):
        apsconfig = {}
        for prop in ["jobstores", "executors"]:
            if isinstance(getattr(config, prop), dict) > 0:
                for prop_name, prop_config in getattr(config, prop).items():
                    apsconfig[".".join(['apscheduler', prop, prop_name])] = prop_config
        apsconfig["apscheduler.job_defaults.coalesce"] = config.coalesce
        apsconfig["apscheduler.job_defaults.max_instances"] = config.max_instances
        apsconfig["apscheduler.timezone"] = config.timezone
        return apsconfig
