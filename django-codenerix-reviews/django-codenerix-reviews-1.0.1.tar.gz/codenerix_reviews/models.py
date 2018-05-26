# -*- coding: utf-8 -*-
from django.conf import settings
from django.db import models
from codenerix.models import CodenerixModel
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.encoding import smart_text
from django.utils.translation import ugettext_lazy as _

from codenerix_invoicing.models_sales import Customer
from codenerix_products.models import ProductFinal


# opiniones sobre productos
# El cliente podrá opinar SOLO sobre productos que haya comprado
class Reviews(CodenerixModel):
    # pasar a person
    customer = models.ForeignKey(Customer, related_name='reviews', verbose_name=_("Customer"), on_delete=models.CASCADE)
    product = models.ForeignKey(ProductFinal, related_name='reviews', verbose_name=_("Product"), on_delete=models.CASCADE)
    stars = models.SmallIntegerField(_("Stars"), validators=[MaxValueValidator(10), MinValueValidator(0)], blank=False, null=False)
    reviews = models.TextField(_("Reviews"), blank=False, null=False)
    validate = models.BooleanField(_("Validate"), blank=True, null=False, default=False)
    # idioma en el que se hace el comentario
    lang = models.CharField(_("Language"), max_length=2, choices=settings.LANGUAGES, blank=False, null=False)

    def __unicode__(self):
        return u"{} ({})".format(smart_text(self.product), smart_text(self.stars))

    def __fields__(self, info):
        fields = []
        fields.append(('customer', _("Customer")))
        fields.append(('product', _("Product")))
        fields.append(('created', _("Date")))
        fields.append(('stars', _("Stars")))
        fields.append(('reviews', _("Reviews")))
        fields.append(('lang', _("Lang")))
        fields.append(('validate', _("Validate")))
        return fields

    def save(self, *args, **kwards):
        if self.pk:
            old = Reviews.objects.get(pk=self.pk)
            product = ProductFinal.objects.get(pk=self.product.pk)
            if old.validate is False and self.validate:
                # new reviews
                value = product.reviews_value * product.reviews_count
                product.reviews_count += 1
                product.reviews_value = (value + self.stars) / product.reviews_count
                product.save()
            elif old.stars != self.stars:
                # edit reviews
                value = (product.reviews_value * product.reviews_count) - old.stars
                product.reviews_value = (value + self.stars) / product.reviews_count
                product.save()
        return super(Reviews, self).save(*args, **kwards)
