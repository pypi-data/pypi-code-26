import io
import boto3
from django.conf import settings
import os
import PIL
import PIL.ImageOps
from url_renditions.models import Rendition
from url_renditions.render import Render
import uuid


s3 = boto3.resource('s3')


def resize_and_upload(input, output, width, height):
    """ reduce image resolution to <constant> precent of what is uploaded """
    image = PIL.Image.open(input)
    if image.mode == "CMYK":
        image = image.convert("RGB")
    if height:
        if height > image.size[1]:
            width = int(image.size[0] * (width / height))
            height = image.size[1]
        elif width > image.size[0]:
            height = int(image.size[1] * (height / width))
            width = image.size[0]
        # crop
        new_image = PIL.ImageOps.fit(
            image,
            (height, width),
            PIL.Image.ANTIALIAS
        )
    else:
        wpercent = (width / float(image.size[0]))
        height = int((float(image.size[1]) * float(wpercent)))
        new_image = image.resize((width, height), PIL.Image.ANTIALIAS)

    out_img = io.BytesIO()
    new_image.save(out_img, 'PNG')
    out_img.seek(0)
    uploaded = s3.Bucket(settings.AWS_STORAGE_BUCKET_NAME).put_object(
        ACL='public-read',
        Key=os.path.join(output, uuid.uuid4().hex + '.png'),
        Body=out_img,
        ContentDisposition='inline',
        ContentType='image/png',
    )
    return {
        'href': 'https://s3.{}.amazonaws.com/{}/{}'.format(
            settings.S3DIRECT_REGION,
            settings.AWS_STORAGE_BUCKET_NAME,
            uploaded.key,
        ),
        'width': width,
        'height': height,
    }


class ResizeImage(Render):

    def __init__(self, size):
        width, height = [d and int(d) or None for d in size.split('x')]
        self.width = width
        self.height = height

    def create_rendition(self, original_file, output):
        rendition_s3 = resize_and_upload(
            input=original_file,
            output=output,
            width=self.width,
            height=self.height,
        )
        return Rendition(**rendition_s3)
