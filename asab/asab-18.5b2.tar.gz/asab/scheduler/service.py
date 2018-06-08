import logging
import aiohttp.web
import aiohttp.web_response
import asab

import crontab

#

L = logging.getLogger(__name__)

#

class SchedulerService(asab.Service):

	def __init__(self, app, service_name):
		super().__init__(app, service_name)


	def crontab(self, crontab_string, funct):
		entry = crontab.CronTab(crontab_string)
