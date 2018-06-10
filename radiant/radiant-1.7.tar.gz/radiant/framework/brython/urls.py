from django.urls import path, include
from django.views.generic import TemplateView

from django.conf.urls.static import static
from django.conf import settings

from .views import BrythonFramework
from .exporter import BrythonExporter

urlpatterns = [

    path('', BrythonFramework.as_view(), name='home'),
    path('system_brython_export', BrythonExporter.as_view(), name='brython_export'),
    path('splash', TemplateView.as_view(template_name="splash.html"), name="splash"),
    path('rdnt/', include('radiant.framework.urls')),

]


try:
    from android.core import main
    main_path = path('system_python', main.Brython.as_view(), name='system_python')
    urlpatterns.insert(2, main_path)
except ImportError as e:
    pass
    print('NO AndroidMain defined!!')

if settings.STATIC_URL and settings.STATIC_ROOT:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)