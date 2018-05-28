from django import template

from wafer.talks.models import TalkType, Track

register = template.Library()


@register.inclusion_tag('wafer.talks/talk_type_block.html')
def talk_types():
    return {
        'types': TalkType.objects.all().order_by('order', 'id'),
    }


@register.inclusion_tag('wafer.talks/talk_track_block.html')
def talk_tracks():
    return {
        'tracks': Track.objects.all().order_by('order', 'id'),
    }
