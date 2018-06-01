from apiclient.discovery import build
from cached_property import cached_property
from googleapiclient.http import MediaInMemoryUpload
from httplib2 import Http
from oauth2client import file, client, tools
import os

from .storage_format import StorageFormat


class DriveStorageFormat(StorageFormat):
    def __init__(self):
        pass

    @property
    def exists(self):
        return self.drive_file is not None

    def read(self):
        if hasattr(self, '_content'):
            return self._content
        if not self.drive_file:
            return None
        self._content = self.service.files().get_media(fileId=self.drive_file['id']).execute()
        return self._content

    def write(self, content):
        if not self.drive_file:
            self.create(content)
        else:
            self.update(content)
        self._content = content

    def create(self, content):
        self._drive_file = self.service.files().create(
            body={
                'name': self.FILENAME,
                'mimeType': 'application/json',
            },
            media_body=MediaInMemoryUpload(content)
        ).execute()

    def update(self, content):
        self.service.files().update(
            fileId=self.drive_file['id'],
            body={
                'name': self.FILENAME,
                'mimeType': 'application/json',
            },
            media_body=MediaInMemoryUpload(content)
        ).execute()

    def clear(self):
        self.service.files().delete(
            fileId=self.drive_file['id']
        ).execute()

    CLIENT_ID = '197003740564-mk25o464aqphqn8ldaernqf8adk7o53n.apps.googleusercontent.com'
    CLIENT_SECRET = 'iR3J72vNO8IdZOteSRkxS2Y_'

    @cached_property
    def service(self):
        store = file.Storage(os.path.expanduser("~/.osafe.json"))
        creds = store.get()
        if not creds or creds.invalid:
            flow = client.OAuth2WebServerFlow(
                client_id=self.CLIENT_ID,
                client_secret=self.CLIENT_SECRET,
                scope='https://www.googleapis.com/auth/drive',
            )
            creds = tools.run_flow(flow, store)
        return build('drive', 'v3', http=creds.authorize(Http()))

    @property
    def drive_file(self):
        if hasattr(self, '_drive_file'):
            return self._drive_file
        result = self.service.files().list(q=f"'root' in parents and name = '{self.FILENAME}' and trashed = false").execute()
        files = result.get('files', ())
        self._drive_file = files[0] if files else None
        return self._drive_file
