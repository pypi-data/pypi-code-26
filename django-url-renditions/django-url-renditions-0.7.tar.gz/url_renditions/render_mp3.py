from django.conf import settings
import os
import io
from url_renditions.models import Rendition
from url_renditions.render import Render
import uuid
from pydub import AudioSegment
import boto3


s3 = boto3.resource('s3')


def generate_mp3(original_file):
    audio = AudioSegment.from_file(original_file)
    out_audio = io.BytesIO()
    audio.export(out_audio)
    out_audio.seek(0)
    return out_audio


def upload_mp3(audio_bin, output):
    uploaded = s3.Bucket(settings.AWS_STORAGE_BUCKET_NAME).put_object(
        ACL='public-read',
        Key=os.path.join(output, uuid.uuid4().hex + '.mp3'),
        Body=audio_bin,
        ContentDisposition='inline',
        ContentType='audio/mp3',
    )
    return 'https://s3.{}.amazonaws.com/{}/{}'.format(
        settings.S3DIRECT_REGION,
        settings.AWS_STORAGE_BUCKET_NAME,
        uploaded.key,
    )


class RenderMp3(Render):

    def create_rendition(self, original_file, output):
        mp3_bin = generate_mp3(original_file)
        href = upload_mp3(mp3_bin, output)
        return Rendition(href=href)
