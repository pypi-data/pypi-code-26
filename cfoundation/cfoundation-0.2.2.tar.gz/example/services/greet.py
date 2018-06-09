from cfoundation import Service

class Greet(Service):
    def english(self):
        log = self.app.log
        c = self.app.conf
        log.info(c.english)

    def french(self):
        log = self.app.log
        c = self.app.conf
        log.info(c.french)

    def german(self):
        log = self.app.log
        c = self.app.conf
        log.info(c.german)

    def spanish(self):
        log = self.app.log
        c = self.app.conf
        log.info(c.spanish)
