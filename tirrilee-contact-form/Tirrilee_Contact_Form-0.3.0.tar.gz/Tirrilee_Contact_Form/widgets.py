from django import forms

class CustomTextInput(forms.TextInput):

    class Media:
        css = {
            'all' : [
                '//stackpath.bootstrapcdn.com/bootstrap/4.1.0/css/bootstrap.min.css'
            ],
        }
        js = [
        ]

    def __init__(self, placeholder='',name=''):
        super(CustomTextInput, self).__init__()
        self.placeholder = placeholder
        self.name = name

    def build_attrs(self, *args, **kwargs):
        context = super().build_attrs(*args, **kwargs)
        context['class'] = 'form-control mt-1'
        context['placeholder'] = self.placeholder
        context['name'] = self.name
        context['style'] = \
            "min-width:200px; " \
            "background-color: " \
            "rgb(242, 237, 233); " \
            "border-color: " \
            "rgb(236, 225, 217); " \
            "font-family: 'Open Sans', 'Nanum Gothic';" \
            "border-radius: 0;"
        return context

class CustomTextarea(forms.Textarea):

    class Media:
        css = {
            'all' : [
                '//stackpath.bootstrapcdn.com/bootstrap/4.1.0/css/bootstrap.min.css'
            ],
        }
        js = [
        ]

    def __init__(self, placeholder='', name=''):
        super(CustomTextarea, self).__init__()
        self.placeholder = placeholder
        self.name = name

    def build_attrs(self, *args, **kwargs):
        context = super().build_attrs(*args, **kwargs)
        context['class'] = 'form-control mt-1'
        context['placeholder'] = self.placeholder
        context['name'] = self.name
        context['style'] = \
            "min-width:200px; " \
            "background-color: " \
            "rgb(242, 237, 233); " \
            "border-color: " \
            "rgb(236, 225, 217); " \
            "font-family: 'Open Sans', 'Nanum Gothic';" \
            "border-radius: 0;"
        return context

class CustomFileInput(forms.FileInput):
    class Media:
        css = {
            'all': [
                '//stackpath.bootstrapcdn.com/bootstrap/4.1.0/css/bootstrap.min.css'
            ],
        }
        js = [
        ]

    def build_attrs(self, *args, **kwargs):
        context = super().build_attrs(*args, **kwargs)
        context['class'] = 'form-control mt-1'
        context['name'] = 'file'
        context['style'] = \
            "min-width:200px; " \
            "background-color: " \
            "rgb(242, 237, 233); " \
            "border-color: " \
            "rgb(236, 225, 217); " \
            "font-family: 'Open Sans', 'Nanum Gothic';" \
            "border-radius: 0;"
        return context
