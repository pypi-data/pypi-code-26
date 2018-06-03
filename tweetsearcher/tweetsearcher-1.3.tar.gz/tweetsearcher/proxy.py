from requests import get


def random_proxy(params=None):
    return get('https://api.getproxylist.com/proxy', params=params).json()
