from cement.core.controller import expose
from cfoundation import Controller

class Base(Controller):
    class Meta:
        label = 'base'
        description = 'Greet'
        arguments = [
            (['--english', '-e'], {
                'action': 'store_true',
                'dest': 'english',
                'help': 'English',
                'required': False
            }),
            (['--french', '-f'], {
                'action': 'store_true',
                'dest': 'french',
                'help': 'French',
                'required': False
            }),
            (['--german', '-g'], {
                'action': 'store_true',
                'dest': 'german',
                'help': 'German',
                'required': False
            }),
            (['--spanish', '-s'], {
                'action': 'store_true',
                'dest': 'spanish',
                'help': 'Spanish',
                'required': False
            })
        ]

    @expose()
    def default(self):
        pargs = self.app.pargs
        s = self.app.services
        if pargs.french:
            return s.greet.french()
        if pargs.german:
            return s.greet.german()
        if pargs.spanish:
            return s.greet.spanish()
        return s.greet.english()
