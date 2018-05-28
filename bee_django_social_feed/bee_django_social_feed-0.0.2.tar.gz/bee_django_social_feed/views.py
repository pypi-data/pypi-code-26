# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import JsonResponse
from bee_django_social_feed.models import Feed
# from django.core.serializers import serialize
from dss.Serializer import serializer
from django.core.paginator import Paginator, EmptyPage

# Create your views here.


def index(request):

    return render(request, 'bee_django_social_feed/index.html', context={
    })


def feeds(request):
    feeds = Feed.objects.order_by('-created_at')
    paginator = Paginator(feeds, 10)
    page = request.GET.get('page')

    try:
        data = paginator.page(page)
    except EmptyPage:
        page = paginator.num_pages
        data = []

    return JsonResponse(data={
        'feeds': serializer(data, output_type='json', datetime_format='string', foreign=True),
        'page': page,
    })


def create_feed(request):
    if request.method == "POST":
        content = request.POST.get('content')
        new_feed = Feed.objects.create(content=content, publisher=request.user)

        return JsonResponse(data={
            'message': 'OK',
            'new_feeds': serializer([new_feed,], output_type='json', datetime_format='string', foreign=True)
        })