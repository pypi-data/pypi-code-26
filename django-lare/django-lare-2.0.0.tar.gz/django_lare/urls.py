from __future__ import unicode_literals

from django import VERSION as DJANGO_VERSION

from django_lare.test_views import *

if DJANGO_VERSION < (1,10):
    from django.conf.urls import patterns, url
    urlpatterns = patterns('',
        url(r'^page1/$',                                Page1View.as_view(),                    name='page_1'),
        url(r'^page1/content1/$',                       Page1Content1View.as_view(),            name='content_1'),
        url(r'^page1/content1/inner_content1/$',        Page1Content1InnerContent1View.as_view(),            name='inner_content_1'),
        url(r'^page1/content1/inner_content2/$',        Page1Content1InnerContent2View.as_view(),            name='inner_content_2'),
        url(r'^page1/content2/$',                       Page1Content2View.as_view(),            name='content_2'),
        url(r'^page2/$',                                Page2View.as_view(),                    name='page_2'),
        url(r'^no-lare-page/$',                         NoLareView.as_view(),                  name='no_lare_page'),
    )
elif DJANGO_VERSION <= (2,0):
    from django.conf.urls import include, url
    urlpatterns = [
        url(r'^page1/$',                                Page1View.as_view(),                    name='page_1'),
        url(r'^page1/content1/$',                       Page1Content1View.as_view(),            name='content_1'),
        url(r'^page1/content1/inner_content1/$',        Page1Content1InnerContent1View.as_view(),            name='inner_content_1'),
        url(r'^page1/content1/inner_content2/$',        Page1Content1InnerContent2View.as_view(),            name='inner_content_2'),
        url(r'^page1/content2/$',                       Page1Content2View.as_view(),            name='content_2'),
        url(r'^page2/$',                                Page2View.as_view(),                    name='page_2'),
        url(r'^no-lare-page/$',                         NoLareView.as_view(),                  name='no_lare_page'),
    ]

else:
    from django.urls import include, re_path
    urlpatterns = [
        re_path(r'^page1/$',                                Page1View.as_view(),                    name='page_1'),
        re_path(r'^page1/content1/$',                       Page1Content1View.as_view(),            name='content_1'),
        re_path(r'^page1/content1/inner_content1/$',        Page1Content1InnerContent1View.as_view(),            name='inner_content_1'),
        re_path(r'^page1/content1/inner_content2/$',        Page1Content1InnerContent2View.as_view(),            name='inner_content_2'),
        re_path(r'^page1/content2/$',                       Page1Content2View.as_view(),            name='content_2'),
        re_path(r'^page2/$',                                Page2View.as_view(),                    name='page_2'),
        re_path(r'^no-lare-page/$',                         NoLareView.as_view(),                  name='no_lare_page'),
    ]
