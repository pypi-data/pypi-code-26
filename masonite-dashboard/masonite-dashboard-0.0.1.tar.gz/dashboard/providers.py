''' A User Model Service Provider '''
from masonite.provider import ServiceProvider
import os
from config.dashboard import MODELS
from .links import ExportLink, ModelLink

package_directory = os.path.dirname(os.path.realpath(__file__))

class DashboardProvider(ServiceProvider):

    wsgi = False 

    def register(self):
        self.app.bind('DashboardModels', MODELS)

        self.app.make('Storage').STATICFILES.update({
            os.path.join(package_directory, 'static/'): '_dashboard/'
        })

        # Register Links:
        self.app.bind('DashboardNavLinks', [ModelLink()])

        Export.register(self.app)

    def boot(self, Storage, ViewClass):
        ViewClass.composer(['/dashboard*'], {'nav_links': self.app.collect('*NavLinks')})

class Export:

    def register(app):
        # app.bind('AnotherProviderNavLinks', [
        #     ExportLink()
        # ])
        pass