from .models import Original
from django.db.models.signals import pre_save
from django.db import models
import io
import requests
import importlib


django_rq = importlib.util.find_spec('django_rq')


def create_renditions(renditions, parent, original, output):
    try:
        Original.objects.get(pk=original.pk)
    except Original.DoesNotExist as e:
        raise e
    original_file = io.BytesIO(requests.get(original.href).content)
    for rendition_name, rendition_creator in renditions.items():
        # returns an unsaved rendition object
        rendition_obj = rendition_creator.create_rendition(original_file=original_file, output=output)
        rendition_obj.original = original
        rendition_obj.name = rendition_name
        rendition_obj.save(force_insert=True)
    original.ready = True
    original.save()


class FileUrlWithRenditions(models.OneToOneField):

    def __init__(self, renditions=None, source=None, output=None, use_job_runner=False, to=Original, null=True, **kwargs):
        self.renditions = renditions
        self.source = source
        self.use_job_runner = use_job_runner
        self.output = output
        kwargs['on_delete'] = models.SET_NULL
        kwargs['blank'] = True
        kwargs['null'] = True
        super(FileUrlWithRenditions, self).__init__(to=to, **kwargs)

    def handle_source_pre_save(self, sender, instance, **kwargs):
        source_file = getattr(instance, self.source)
        original_obj = getattr(instance, self.name)
        if not original_obj or original_obj.href != source_file:
            if original_obj:
                original_obj.delete()
                # FIXME: WHY ? maybe original_obj is not what it was when we used post_save
                setattr(instance, self.name, None)
            if not source_file:
                return
            original_obj = Original.objects.create(href=source_file)
            setattr(instance, self.name, original_obj)
            # create renditions
            props = dict(renditions=self.renditions, output=self.output, parent=instance, original=original_obj)
            if django_rq and self.use_job_runner:
                django_rq.enqueue(create_renditions, **props)
            else:
                create_renditions(**props)

    def contribute_to_class(self, cls, name):
        super(FileUrlWithRenditions, self).contribute_to_class(cls, name)
        self.remote_field.related_name = '{}_{}'.format(cls.__name__, name)
        pre_save.connect(self.handle_source_pre_save, sender=cls)
