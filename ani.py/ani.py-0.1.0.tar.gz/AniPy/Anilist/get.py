import json
import time

import requests

from AniPy.errors import AniPyImplementationError


class Get:
    def __init__(self, settings):
        self.settings = settings
        self.session = requests.session()

        self.remaining = 90
        self.limit = 90
        self.reset = time.time()

    def fetch(self, element):
        request = element.query()

        request = """\
        query($id: Int) {
        """ + type(element).__name__ + """(id: $id, type: ANIME)
        """ + request + "}"

        vars = {"id": element.id}

        if self.remaining == 0:
            time.sleep(max(self.reset - time.time(), 0))

        r = self.session.post(self.settings["apiurl"],
                              headers=self.settings["header"],
                              json={"query": request, "variables": vars})

        jsd = json.loads(r.text)

        self.limit = int(r.headers.get("x-ratelimit-limit"))
        self.remaining = int(r.headers.get("x-ratelimit-remaining"))
        self.reset = int(r.headers.get("X-RateLimit-Reset"))

        print(self.remaining, "/", self.limit, ",", self.reset, time.time())

        if len(jsd.get("errors", [])) > 0:
            print(request)
            raise AniPyImplementationError(str(jsd["errors"][0]))

        return element.fill(jsd["data"][type(element).__name__], "")
