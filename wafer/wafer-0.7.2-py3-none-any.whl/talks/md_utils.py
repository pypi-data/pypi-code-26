# Wrapper functions to call our template tags for use as markdown variables


def talk_types_list():
    from .models import TalkType
    result = ['<ul>']
    for talktype in TalkType.objects.all().order_by('order', 'id'):
        result.append('<li>%s &mdash; %s</li>' % (talktype.name, talktype.description))
    result.append('</ul>')
    return '\n'.join(result)


def talk_tracks_list():
    from .models import Track
    result = []
    for track in Track.objects.all().order_by('order', 'id'):
        result.append('  * %s - %s' % (track.name, track.description))
    return '\n\n'.join(result)
