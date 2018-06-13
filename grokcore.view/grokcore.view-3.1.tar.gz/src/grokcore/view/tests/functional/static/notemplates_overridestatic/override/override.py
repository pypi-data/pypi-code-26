

from grokcore import view as grok
from grokcore.view.tests.functional.static.notemplates_overridestatic.original.original import CaveView


class StaticResource(grok.DirectoryResource):
    grok.name('grokcore.view.tests.functional.static.notemplates_overridestatic.override')
    grok.path('static')


class PalaceView(CaveView):
    pass
