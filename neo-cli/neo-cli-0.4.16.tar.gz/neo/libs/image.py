from neo.libs import login as login_lib
from glanceclient import Client as image_client


def get_image_client():
    img = image_client('2', session=login_lib.get_session())
    return img


def get_list():
    img = get_image_client()
    return img.images.list()


def detail(image_id):
    img = get_image_client()
    return img.images.get(image_id)
