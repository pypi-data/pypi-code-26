from AniPy.Anilist.get import Get
from AniPy.Anilist.search import Search


class Anilist:

    def __init__(self, cid=None, csecret=None, credentials=None):
        self.settings = {
            "header": {
                "Content-Type": "application/json",
                "User-Agent": "ani.py (git.widmer.me/project/multimedia/ani.py)",
                "Accept": "application/json"
            },
            'authurl': 'https://anilist.co/api',
            'apiurl': 'https://graphql.anilist.co',
            'cid': cid,
            'csecret': csecret,
            'token': credentials
        }

        self.search = Search(self.settings, self)
        self.get = Get(self.settings)
