from django.core.management.base import BaseCommand, CommandError
from django.apps import apps
import sys, re
class Command(BaseCommand):
    help = 'Generate models, serializers and urls'
    # /{app}/views.py
    viewsets_imports = """
from rest_framework import viewsets
from rest_framework import permissions
"""

    viewsets_template_1 = """from .models import {model}
    """

    viewsets_template_2 = """from .serializers import {model}Serializer
    """

    viewsets_template_3 = """
class {model}ViewSet(viewsets.ModelViewSet):
    queryset = {model}.objects.all()
    serializer_class = {model}Serializer
    permission_classes = (permissions.IsAuthenticated,)
    """

    # /{app}/serializers.py
    serializers_imports = """
from rest_framework import serializers
from .models import {model}
    """

    serializers_template_1 = """
class {model}Serializer(serializers.ModelSerializer):
    class Meta:
        model = {model}
        fields = "__all__"
    """
    # {project}/{app}/urls.py
    urls_imports = """
from django.conf.urls import url, include
from rest_framework import routers
from . import views
    """

    urls_template_1 = """
router = routers.DefaultRouter()"""


    urls_template_2 = """
router.register(
    "{model_lower}",
    views.{model}ViewSet,
    base_name="{model_lower}",
)
"""

    urls_template_3 = """
urlpatterns = [
    url(r"^", include(router.urls)),
]
    """
    # {app}/models.py
    models_import = """
from django.db import models
"""

    models_template_1 = """class {model}(models.Model):
    pass
    """
    
    admin_imports = """
from .models import {model}
"""
    admin_template_1 = """
class {model}Admin(admin.ModelAdmin):
    model = {model}
admin.site.register({model}, {model}Admin)
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
        model = options["model"].capitalize()
        if(not app or not model):
            print("Please fill both app and model params")
        else :
            print('Generating {} CommandError for app {}'.format(model, app))


            modules = [
                ('models.py', self.generate_models(app,model), "{}/{}".format(app,"models.py") ),
                ('views.py', self.generate_views(app,model), "{}/{}".format(app,"views.py")),
                ('serializers.py', self.generate_serializers(app, model), "{}/{}".format(app,"serializers.py")),
                ('urls.py', self.generate_urls(app, model), "{}/{}".format(app,"urls.py")),
                ('admin.py', self.generate_admin(app, model), "{}/{}".format(app,"admin.py")),
            ]

            for name, code, file in modules:
                print(code)
                boilerplate = ""
                #boilerplate += "# {}".format(name)
                imports = code[0]
                boilerplate += code[1]
                boilerplate += "\n"
                boilerplate += "\n"
                if not options["dry-run"] : # Add imports top
                    f = open(file, "r")
                    content = f.read()
                    f.close()
                    f = open(file, "w+")
                    f.write(imports)
                    f.write(content)
                    f.close()
                if not options["dry-run"] : # Add code bottom
                    f = open(file, "a+")
                    f.write(boilerplate)
                sys.stdout.write(imports)
                sys.stdout.write(boilerplate)

    # def write_if_not_exists(self, app, name, content):
    #     with open("{}/{}".format(app,name)) as fo:
    #         content_as_string = fo.read().strip()
    #         match = re.findall(content.strip(), content_as_string, re.S)
    #         print("{} for {}".format(match, content))

    def generate_models(self, app, model):
        # print(self.write_if_not_exists(app, "models.py", self.models_template_1.format(app=app, model=model)))
        imports = self.models_import.format(app=app, model=model)
        # print(self.write_if_not_exists(app, "models.py", self.models_template_1.format(app=app, model=model)))
        code = self.models_template_1.format(app=app, model=model)
        return (imports, code)

    def generate_views(self, app, model):
        imports = self.viewsets_imports.format(app=app, model=model)
        code = self.viewsets_template_1.format(app=app, model=model)
        code += "\n"
        code += self.viewsets_template_2.format(app=app, model=model)
        code += self.viewsets_template_3.format(app=app, model=model)
        return (imports, code)

    def generate_serializers(self, app, model):
        imports = self.serializers_imports.format(app=app, model=model)
        code = self.serializers_template_1.format(app=app, model=model)
        return (imports, code)

    def generate_urls(self, app, model):
        imports = self.urls_imports.format(app=app, model=model)
        code = self.urls_template_1.format(app=app, model=model)
        code += self.urls_template_2.format(app=app, model=model, model_lower=model.lower())
        code += self.urls_template_3.format(app=app, model=model)
        return (imports, code)
    def generate_admin(self, app, model):
        imports = self.admin_imports.format(app=app, model=model)

        code = self.admin_template_1.format(app=app, model=model)
        return (imports, code)
       