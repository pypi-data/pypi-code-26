from . import api,models


def create_folder(name):
    res = api.create_folder(name)
    if res:
        folder = models.FolderGrafana(folder_id=res['id'],folder_uid=res['uid'],name=name)
        folder.save()