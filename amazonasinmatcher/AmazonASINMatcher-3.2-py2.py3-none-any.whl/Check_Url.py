import requests


def check_url(url):
    try:
        request = requests.get(url)
        if request.status_code == 200:
            return True
    except:
        return False
    return False
