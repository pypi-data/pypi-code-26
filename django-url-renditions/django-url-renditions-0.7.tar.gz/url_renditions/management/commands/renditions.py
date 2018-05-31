from django.core.management.base import BaseCommand
from django.apps import apps
from url_renditions.fields import FileUrlWithRenditions


class Command(BaseCommand):
    help = 'Reset renditions'

    def add_arguments(self, parser):
        parser.add_argument('models', nargs='+', type=str)

    def handle(self, *args, **options):
        for model in options['models']:
            self.stdout.write('Model {}'.format(model))
            Model = apps.get_model(model)
            fields_to_reset = [f for f in Model._meta.get_fields() if type(f) is FileUrlWithRenditions]
            for o in Model.objects.all():
                to_be_saved = False
                for field in fields_to_reset:
                    if getattr(o, field.source):
                        to_be_saved = True
                        self.stdout.write('reset field {} of {}'.format(field, o))
                        if getattr(o, field.name):
                            getattr(o, field.name).delete()
                            setattr(o, field.name, None)
                if to_be_saved:
                    o.save()
