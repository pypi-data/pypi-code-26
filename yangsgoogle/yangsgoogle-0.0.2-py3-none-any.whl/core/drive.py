from yangsgoogle.credentials import CredentialManager, ServiceMap
from yangsutil import LogUtil, FileUtil
from googleapiclient.http import MediaIoBaseDownload
import io

SERVICE = {
    'version': 'v3',
    'scope': [
        'https://www.googleapis.com/auth/drive'
    ]
}


# TODO : Google Drive
class YangsGoogleDrive:

    def __init__(self, app_name, user_name, credential_root, logger=None):
        self.logger = LogUtil.get_logger(app_name=app_name) if logger is None else logger

        self.service = CredentialManager(logger=self.logger).service(
            service_name=ServiceMap.SHEETS,
            app_name=app_name,
            user_name=user_name,
            credential_root=credential_root
        )

    # public
    def download(self, file_id, file_type, file_path):
        FileUtil.make_folder(file_path)

        request = self.service.files().export_media(fileId=file_id, mimeType=file_type)

        fh = io.FileIO(file_path, 'wb')
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            self.logger.info("Download %d%%." % int(status.progress() * 100))
