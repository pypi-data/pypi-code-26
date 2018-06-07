import io
from http.client import BAD_REQUEST, FORBIDDEN, NOT_FOUND, OK

from PIL import Image


def _open_image_data(data):
    return Image.open(io.BytesIO(data))


def test_image_can_be_proxied(client, bucket_name):
    resp = client.get('/{}/pics/image-600x400.jpg'.format(bucket_name))
    assert resp.status_code == OK
    assert resp.content_type == 'image/jpeg'
    img = _open_image_data(resp.data)
    assert img.size == (600, 400)
    assert img.format == 'JPEG'


def test_image_can_be_resized_to_exact_size(client, bucket_name):
    resp = client.get('/{}/pics/image-600x400.jpg?w=50&h=50'
                      .format(bucket_name))
    assert resp.status_code == OK
    assert resp.content_type == 'image/jpeg'
    img = _open_image_data(resp.data)
    assert img.size == (50, 50)
    assert img.format == 'JPEG'


def test_image_can_be_upscaled(client, bucket_name):
    resp = client.get('/{}/pics/image-20x13.jpg?w=50&h=50'
                      .format(bucket_name))
    assert resp.status_code == OK
    assert resp.content_type == 'image/jpeg'
    img = _open_image_data(resp.data)
    assert img.size == (50, 50)
    assert img.format == 'JPEG'


def test_image_not_found_returns_404(client, bucket_name):
    resp = client.get('/{}/pics/does-not-exist.jpg'
                      .format(bucket_name))
    assert resp.status_code == NOT_FOUND
    assert resp.content_type == 'text/html'
    assert 'Image not found' in resp.data.decode()


def test_invalid_bucket_returns_403(client, bucket_name):
    resp = client.get('/INVALID/pics/image-20x13.jpg?w=50&h=50')
    assert resp.status_code == FORBIDDEN
    assert resp.content_type == 'text/html'
    assert 'Cannot access bucket' in resp.data.decode()


def test_bad_arg_returns_400(client, bucket_name):
    resp = client.get('/{}/pics/image-20x13.jpg?w=HELLO'
                      .format(bucket_name))
    assert resp.status_code == BAD_REQUEST
    assert resp.content_type == 'text/html'
    assert 'Parameter w must be an integer' in resp.data.decode()


def test_arg_out_of_bounds_returns_400(client, bucket_name):
    resp = client.get('/{}/pics/image-20x13.jpg?w=9999999999'
                      .format(bucket_name))
    assert resp.status_code == BAD_REQUEST
    assert resp.content_type == 'text/html'
    assert 'Parameter w out of bounds' in resp.data.decode()


def test_png_image_indexed_can_be_converted(client, bucket_name):
    resp = client.get('/{}/pics/image-mode-P.png?w=50&h=50'
                      .format(bucket_name))
    assert resp.status_code == OK
    assert resp.content_type == 'image/jpeg'
    img = _open_image_data(resp.data)
    assert img.size == (50, 50)
    assert img.mode == 'RGB'
    assert img.format == 'JPEG'
