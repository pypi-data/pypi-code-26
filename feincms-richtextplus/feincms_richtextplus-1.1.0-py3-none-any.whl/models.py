from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.db.models import AutoField
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

from feincms.content.richtext.models import RichTextContent


class RichTextPlusContent(RichTextContent):
    class Meta:
        abstract = True
        verbose_name = _('RichText+')
        verbose_name_plural = _('RichTexts+')

    @classmethod
    def rt_to_rtplus(cls, bases):
        for base in bases:
            for p in base.objects.all():
                rts = p.content.all_of_type(RichTextContent)
                for rt in rts:
                    exclude = ('id', )
                    initial = dict(
                        (f.name, getattr(rt, f.name)) for f in rt._meta.fields
                        if not isinstance(f, AutoField) and f.name not in exclude
                        and f not in rt._meta.parents.values())
                    rtplus_cls_concrete = base.content_type_for(cls)
                    try:
                        rtplus = rtplus_cls_concrete(**initial)
                    except TypeError:
                        raise ImproperlyConfigured(
                            '%s class has no %s attached to it' % (
                                base.__name__,
                                cls.__name__,
                            )
                        )
                    # rtplus = copy_model_instance(rt, exclude=('id'))
                    # rtplus.text = rt.text
                    # rtplus.id = None
                    # NOTE: replace with your default type
                    rtplus.type = 'default'
                    # save our new RichTextPlusContent with data from its original
                    # RichTextContent counterpart
                    rtplus.save()
                    # delete original
                    rt.delete()

    @classmethod
    def initialize_type(cls, cleanse=None, TYPE_CHOICES=None):
        super(RichTextPlusContent, cls).initialize_type(cleanse=cleanse)
        if TYPE_CHOICES is None:
            raise ImproperlyConfigured(
                'You have to set TYPE_CHOICES when'
                ' creating a %s' % cls.__name__)

        cls.add_to_class(
            'type',
            models.CharField(
                _('type'),
                max_length=20,
                choices=TYPE_CHOICES,
                default=TYPE_CHOICES[0][0],
            )
        )

    def render(self, **kwargs):
        ctx = {'content': self}
        ctx.update(kwargs)

        return render_to_string([
            'content/richtextplus/%s.html' % self.type,
            'content/richtextplus/default.html',
        ], ctx)
