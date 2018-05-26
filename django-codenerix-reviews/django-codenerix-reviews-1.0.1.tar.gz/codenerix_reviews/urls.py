# -*- coding: utf-8 -*-
from django.conf.urls import url
from codenerix_reviews.views import ReviewsList, ReviewsUpdate, ReviewsUpdateModal, ReviewsDelete, ReviewsSubList, ReviewsDetails, ReviewsDetailModal, ReviewsCreate, ReviewsCreateModal


urlpatterns = [
    url(r'^reviews$', ReviewsList.as_view(), name='CDNX_reviews_reviewss_list'),
    url(r'^reviews/add$', ReviewsCreate.as_view(), name='CDNX_reviews_reviewss_add'),
    url(r'^reviews/addmodal$', ReviewsCreateModal.as_view(), name='CDNX_reviews_reviewss_addmodal'),
    url(r'^reviews/(?P<pk>\w+)$', ReviewsDetails.as_view(), name='CDNX_reviews_reviewss_details'),
    url(r'^reviews/(?P<pk>\w+)/edit$', ReviewsUpdate.as_view(), name='CDNX_reviews_reviewss_edit'),
    url(r'^reviews/(?P<pk>\w+)/editmodal$', ReviewsUpdateModal.as_view(), name='CDNX_reviews_reviewss_editmodal'),
    url(r'^reviews/(?P<pk>\w+)/delete$', ReviewsDelete.as_view(), name='CDNX_reviews_reviewss_delete'),
    url(r'^reviews/(?P<pk>\w+)/sublist$', ReviewsSubList.as_view(), name='CDNX_reviews_reviewss_sublist'),
    url(r'^reviews/(?P<pk>\w+)/sublist/add$', ReviewsCreateModal.as_view(), name='CDNX_reviews_reviewss_sublist_add'),
    url(r'^reviews/(?P<cpk>\w+)/sublist/(?P<pk>\w+)$', ReviewsDetailModal.as_view(), name='CDNX_reviews_reviewss_sublist_details'),
    url(r'^reviews/(?P<cpk>\w+)/sublist/(?P<pk>\w+)/edit$', ReviewsUpdateModal.as_view(), name='CDNX_reviews_reviewss_sublist_details'),
    url(r'^reviews/(?P<cpk>\w+)/sublist/(?P<pk>\w+)/delete$', ReviewsDelete.as_view(), name='CDNX_reviews_reviewss_sublist_delete'),
]
