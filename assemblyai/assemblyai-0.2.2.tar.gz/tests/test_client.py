"""Tests for client."""

import os

import pytest

from assemblyai import Client
from assemblyai.exceptions import ClientError
# import wikipedia


ASSEMBLYAI_URL = os.environ.get('ASSEMBLYAI_URL', 'https://api.assemblyai.com')
ASSEMBLYAI_TOKEN = os.environ.get('ASSEMBLYAI_TOKEN')
AUDIO_URL = ('https://s3-us-west-2.amazonaws.com/'
             'assemblyai.prooflab/office_nine_degrees.wav')


def test_client_auth_error():
    """Test client without token throws auth error."""
    with pytest.raises(ClientError):
        aai = Client(token='foobar')
        aai.transcribe(audio_url=AUDIO_URL)


def test_client_transcribe():
    """Test client token authenticates and creates transcript."""
    aai = Client(token=ASSEMBLYAI_TOKEN)
    transcript = aai.transcribe(audio_url=AUDIO_URL)
    assert transcript.status == 'queued'
    transcript_id = transcript.id
    while transcript.status != 'completed':
        transcript = transcript.get()
    assert transcript.status == 'completed'
    assert transcript_id == transcript.id
    transcript = transcript.get(id=transcript_id)
    assert transcript_id == transcript.id


def test_client_train():
    """Test client token authenticates and creates transcript."""
    aai = Client(token=ASSEMBLYAI_TOKEN)
    model = aai.train(['foo', 'bar'])
    assert model.status == 'training'
    model_id = model.id
    model = model.get()
    assert model_id == model.id


def test_client_train_transcribe():
    """Test client token authenticates and creates transcript."""
    aai = Client(token=ASSEMBLYAI_TOKEN)
    model = aai.train(['foo', 'bar'])
    assert model.status == 'training'
    model_id = model.id
    model = model.get()
    assert model_id == model.id
    model = model.get(id=model_id)
    assert model_id == model.id
    transcript = aai.transcribe(audio_url=AUDIO_URL, model=model)
    assert transcript.id is None
    transcript = transcript.get()
    assert transcript.id is None
    assert transcript.status == 'waiting for model'


def test_client_transcribe_mono_speaker_count_invalid():
    """Test client token authenticates and creates transcript."""
    aai = Client(token=ASSEMBLYAI_TOKEN)
    transcript = aai.transcribe(audio_url=AUDIO_URL, speaker_count=2)
    assert transcript.status == 'queued'
    transcript_id = transcript.id
    while transcript.status != 'completed':
        transcript = transcript.get()
    assert transcript.status == 'completed'
    assert transcript_id == transcript.id
    transcript = transcript.get(id=transcript_id)
    assert transcript_id == transcript.id
    assert transcript.speaker_count == 2


def test_client_transcribe_format_text_false():
    """Test client token authenticates and creates transcript."""
    aai = Client(token=ASSEMBLYAI_TOKEN)
    transcript = aai.transcribe(audio_url=AUDIO_URL, format_text=False)
    assert transcript.status == 'queued'
    transcript_id = transcript.id
    while transcript.status != 'completed':
        transcript = transcript.get()
    assert transcript.status == 'completed'
    assert transcript_id == transcript.id
    transcript = transcript.get(id=transcript_id)
    assert transcript_id == transcript.id
    assert transcript.format_text is False
