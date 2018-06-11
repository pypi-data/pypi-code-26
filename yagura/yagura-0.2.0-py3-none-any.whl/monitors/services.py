from django.utils.timezone import now
from urllib.error import HTTPError, URLError
from urllib.request import urlopen
from .models import Target, TargetState


def save_state(target: Target, state: str) -> TargetState:
    """Save state object for current state
    """
    last = target.states.last()
    if last is None:
        current = TargetState.objects.create(target=target, state=state)
    elif last.state == state:
        last.updated_at = now()
        last.save()
        current = last
    else:
        last.end_at = last.updated_at = now()
        last.save()
        current = TargetState.objects.create(target=target, state=state)
    return current


def try_monitor(url: str) -> str:
    """Request HTTP and return result

    Return 'OK' if request has response and status-code is 200
    """
    try:
        resp = urlopen(url)
    except HTTPError as err:
        return 'NG'
    except URLError as err:
        return 'NG'
    return 'OK' if resp.code == 200 else 'NG'
