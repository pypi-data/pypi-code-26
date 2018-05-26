# -*- coding: utf-8 -*-
from django.conf import settings
from django.db.models import Q
from django.utils.translation import ugettext as _

from codenerix.views import GenList, GenCreate, GenCreateModal, GenUpdate, GenUpdateModal, GenDelete, GenDetail, GenDetailModal

from codenerix_reviews.models import Reviews
from codenerix_reviews.forms import ReviewsForm


# ###########################################
class GenReviewsUrl(object):
    ws_entry_point = '{}/reviews'.format(settings.CDNX_REVIEWS)


# Reviews
class ReviewsList(GenReviewsUrl, GenList):
    model = Reviews
    linkadd = False
    show_details = True
    extra_context = {'menu': ['Reviews', 'people'], 'bread': [_('Reviews'), _('People')]}


class ReviewsCreate(GenReviewsUrl, GenCreate):
    model = Reviews
    form_class = ReviewsForm
    show_details = True

    @property
    def lang(self):
        lang = None
        for x in settings.LANGUAGES:
            if x[0] == self.request.LANGUAGE_CODE:
                return self.request.LANGUAGE_CODE.lower()
        return settings.LANGUAGES[0][0].lower()

    def get_form_kwargs(self):
        kwargs = super(ReviewsCreate, self).get_form_kwargs()

        customer = self.request.user.person.customer

        kwargs['data']['customer'] = customer.pk
        kwargs['data']['lang'] = self.lang

        return kwargs


class ReviewsCreateModal(GenCreateModal, ReviewsCreate):
    pass


class ReviewsUpdate(GenReviewsUrl, GenUpdate):
    model = Reviews
    form_class = ReviewsForm
    show_details = True


class ReviewsUpdateModal(GenUpdateModal, ReviewsUpdate):
    pass


class ReviewsDelete(GenReviewsUrl, GenDelete):
    model = Reviews


class ReviewsSubList(GenReviewsUrl, GenList):
    model = Reviews
    show_details = False
    json = False
    template_model = "reviews/reviews_sublist.html"
    extra_context = {'menu': ['Reviews', 'people'], 'bread': [_('Reviews'), _('People')]}

    def __limitQ__(self, info):
        limit = {}
        pk = info.kwargs.get('pk', None)
        limit['link'] = Q(customer__pk=pk)
        return limit


class ReviewsDetails(GenReviewsUrl, GenDetail):
    model = Reviews
    groups = ReviewsForm.__groups_details__()


class ReviewsDetailModal(GenDetailModal, ReviewsDetails):
    pass
