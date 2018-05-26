# -*- coding: utf-8 -*-
from django.utils.translation import ugettext as _
from codenerix.forms import GenModelForm
from codenerix_reviews.models import Reviews


class ReviewsForm(GenModelForm):
    class Meta:
        model = Reviews
        exclude = []

    def __groups__(self):
        g = [
           (_('Details'), 12,
                ['customer', 6],
                ['product', 6],
                ['stars', 6],
                ['reviews', 6],
                ['lang', 6],
                ['validate', 6],
            )
        ]
        return g

    @staticmethod
    def __groups_details__():
        g = [
           (_('Details'), 12,
                ['customer', 6],
                ['product', 6],
                ['stars', 6],
                ['reviews', 6],
                ['lang', 6],
                ['validate', 6],
            )
        ]
        return g
