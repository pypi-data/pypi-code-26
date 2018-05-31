import logging

from defpi.ConnectionHandlerManager import ConnectionHandlerManager
from defpi.ConnectionManager import ConnectionManager
from defpi.Exceptions import ServiceInvocationException
from defpi.Service import Service
from defpi.ServiceExecutor import ServiceExecutor
from defpi.ServiceManager import ServiceManager


class ServiceMain:
    logger = logging.getLogger('defpi.ServiceMain')
    threadCount = 0
    serviceExecutor = ServiceExecutor.getInstance()

    def getServiceClass(self):
        service_impls = Service.__subclasses__()
        if len(service_impls) > 1:
            raise ServiceInvocationException('Unable to start service, more than 1 service implementation found')
        if len(service_impls) < 1:
            raise ServiceInvocationException('Unable to start service, no service implementations found')

        return service_impls[0]

    @staticmethod
    def registerMessageHandlers(service: Service):
        managers = ConnectionHandlerManager.__subclasses__()

        if len(managers) < 1:
            ServiceMain.logger.error("No ConnectionHandlerManager implementations found")

        for managerClass in managers:
            if len(managerClass.__subclasses__()) == 1:
                managerClassImpl = managerClass.__subclasses__()[0]

                manager = ServiceMain.instantiateManagerWithService(managerClassImpl, service)
                if manager is None:
                    continue
                try:
                    methodList = [getattr(managerClassImpl, func) for func
                                  in dir(managerClassImpl) if callable(getattr(managerClassImpl, func))]
                    for method in methodList:
                        if method.__name__.startswith('build') and \
                                hasattr(method, '__annotations__') and \
                                len(method.__annotations__) == 2:
                            ConnectionManager.registerConnectionHandlerFactory(method.__annotations__['return'], manager)
                except Exception as e:
                    ServiceMain.logger.warning("Unable to instantiate manager type {} of service {}: {}"
                                               .format(managerClassImpl, service, e))
                    continue

    @staticmethod
    def instantiateManagerWithService(managerClass, service: Service) -> ConnectionHandlerManager:
        try:
            return managerClass(service)
        except Exception as e:
            ServiceMain.logger.warning("Exception while creating instance of {}: {}".format(managerClass, e))

        ServiceMain.logger.debug("Attempting fallback empty constructor for {}".format(managerClass))
        try:
            return managerClass()
        except Exception as e:
            ServiceMain.logger.warning("Exception while creating instance of {} with empty constructor: {}".format(
                managerClass, e))
        return None

    def main(self, serviceClass):
        manager = ServiceManager()

        def futureFn():
            try:
                # serviceClass = self.getServiceClass()
                service = serviceClass()
                self.registerMessageHandlers(service)
                ServiceMain.logger.debug("ConnectionHandlers: {}".format(ConnectionManager.connectionHandlers))
                ServiceMain.logger.debug("InterfaceInfo: {}".format(ConnectionManager.interfaceInfo))
                manager.start(service)
            except BaseException as e:
                self.logger.error("Error while starting service: {}".format(e))
                manager.close()

        ServiceMain.serviceExecutor.submit(futureFn)
        manager.join()
