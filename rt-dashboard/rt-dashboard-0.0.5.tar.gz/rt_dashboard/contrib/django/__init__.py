from django.apps import AppConfig
from django.http import HttpResponse, HttpResponseNotFound
from rt_dashboard.web import app
from django.shortcuts import render


class Dashboard(AppConfig):
    name = 'rt_dashboard.contrib.django'
    label = 'rt_dashboard'


def get_admin_view(base_path):
    if base_path[-1] == '/':
        base_path = base_path[:-1]

    base_view = get_view(base_path + '/inner')

    def view(request):
        if not request.path.startswith(base_path):
            return HttpResponseNotFound()
        path = request.path[len(base_path):]
        if path.startswith('/inner'):
            return base_view(request)
        else:
            return render(request, 'rt_dashboard_admin.html', {
                'title': 'RT Dashboard',
                'iframe_src': base_path + '/inner/',
            })

    return view


def get_view(base_path):
    if base_path[-1] == '/':
        base_path = base_path[:-1]

    def view(request):
        if not request.path.startswith(base_path):
            return HttpResponseNotFound()
        path = request.path[len(base_path):]
        resp = app.get_response(request.get_host(),
                                path,
                                method=request.method,
                                base_path=base_path)
        response = HttpResponse(resp.data, status=resp.status_code)
        for header, value in resp.headers.items():
            response[header] = value
        return response

    return view
