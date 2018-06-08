import logging
import asab

from .service import SchedulerService

#

L = logging.getLogger(__name__)

#

class Module(asab.Module):

	def __init__(self, app):
		super().__init__(app)
		self.service = SchedulerService(app, "asab.SchedulerService")
