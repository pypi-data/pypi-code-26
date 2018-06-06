from django.core.management.base import BaseCommand, CommandError
from django.apps import apps
import sys, re
class Command(BaseCommand):
    help = 'Generate models, serializers and urls'
    # /{app}/views.py
    viewsets_template_1 = """
from rest_framework import viewsets
from rest_framework import permissions
"""

    viewsets_template_2 = """from .models import {model}
    """

    viewsets_template_3 = """from .serializers import {model}Serializer
    """

    viewsets_template_4 = """
class {model}ViewSet(viewsets.ModelViewSet):
    queryset = {model}.objects.all()
    serializer_class = {model}Serializer
    permission_classes = (permissions.IsAuthenticated,)
    """

    # /{app}/serializers.py
    serializers_template_1 = """
from rest_framework import serializers
    """

    serializers_template_2 = """
from .models import {model}
    """

    serializers_template_3 = """
class {model}Serializer(serializers.ModelSerializer):
    class Meta:
        model = {model}
        fields = "__all__"
    """
    # {project}/{app}/urls.py
    urls_template_1 = """
from django.conf.urls import url, include
from rest_framework import routers
from . import views
    """

    urls_template_2 = """
router = routers.DefaultRouter()"""


    urls_template_3 = """
router.register(
    "{model}",
    views.{model}ViewSet,
    base_name="{model}",
)
"""

    urls_template_4 = """
urlpatterns = [
    url(r"^", include(router.urls)),
]
    """
    # {app}/models.py
    models_template_1 = """
from django.db import models
"""

    models_template_2 = """class {model}(models.Model):
    pass
    """

    def add_arguments(self, parser):

        parser.add_argument(
            'app',
            help='App Name',
            type=str
        )
        parser.add_argument(
            'model',
            type=str,
            help='Model Name',
        )
        parser.add_argument('--dry-run', action='store_true', dest='dry-run', default=False, help=u'Only print and do not write onto files')

    def handle(self, *args, **options):
        app = options["app"] if options["app"] else None
        # Make model Capitalize
        model = options["model"]
        if(not app or not model):
            print("Please fill both app and model params")
        else :
            print('Generating {} model for app {}'.format(model, app))


            modules = [
                ('models.py', self.generate_models(app,model), "{}/{}".format(app,"models.py") ),
                ('views.py', self.generate_views(app,model), "{}/{}".format(app,"views.py")),
                ('serializers.py', self.generate_serializers(app, model), "{}/{}".format(app,"serializers.py")),
                ('urls.py', self.generate_urls(app, model), "{}/{}".format(app,"urls.py")),
            ]

            for name, code, file in modules:
                boilerplate = ""
                #boilerplate += "# {}".format(name)
                boilerplate += code
                boilerplate += "\n"
                boilerplate += "\n"
                if not options["dry-run"] :
                    f = open(file, "a+")
                    f.write(boilerplate)
                sys.stdout.write(boilerplate)

    # def write_if_not_exists(self, app, name, content):
    #     with open("{}/{}".format(app,name)) as fo:
    #         content_as_string = fo.read().strip()
    #         match = re.findall(content.strip(), content_as_string, re.S)
    #         print("{} for {}".format(match, content))

    def generate_models(self, app, model):
        # print(self.write_if_not_exists(app, "models.py", self.models_template_1.format(app=app, model=model)))
        models = self.models_template_1.format(app=app, model=model)
        # print(self.write_if_not_exists(app, "models.py", self.models_template_2.format(app=app, model=model)))
        models += self.models_template_2.format(app=app, model=model)

        return models
    def generate_views(self, app, model):
        views = self.viewsets_template_1.format(app=app, model=model)
        views += self.viewsets_template_2.format(app=app, model=model)
        views += "\n"
        views += self.viewsets_template_3.format(app=app, model=model)
        views += self.viewsets_template_4.format(app=app, model=model)
        return views

    def generate_serializers(self, app, model):
        serializers = self.serializers_template_1.format(app=app, model=model)
        serializers += self.serializers_template_2.format(app=app, model=model)
        serializers += self.serializers_template_3.format(app=app, model=model)
        return serializers

    def generate_urls(self, app, model):
        urls = self.urls_template_1.format(app=app, model=model)
        urls += self.urls_template_2.format(app=app, model=model)
        urls += self.urls_template_3.format(app=app, model=model)
        urls += self.urls_template_4.format(app=app, model=model)
        return urls
       