from datetime import datetime

from igamelister.amiga.chipset import Chipset
from igamelister.amiga.person import Person
from igamelister.amiga.publisher import Publisher
from igamelister.webscraper.template import Template


class LemonAmiga:
    def __init__(self, page_id: int):
        tmp = Template("lemonamiga.ini", page_id=page_id)

        def add_people(people: list, role: str):
            r = []
            for person in people:
                r.append(Person(person, role))
            return r

        def add_chipsets(c: list) -> list:
            r = []
            for x in c:
                if x == "OCS":
                    r.append(Chipset.OCS)
                elif x == "ECS":
                    r.append(Chipset.ECS)
                elif x == "AGA":
                    r.append(Chipset.AGA)
                elif x == "CD32":
                    r.append(Chipset.CD32)
                elif x == "CDTV":
                    r.append(Chipset.CDTV)
                elif x == "CD-ROM":
                    r.append(Chipset.AmigaCD)
                elif x == "Arcadia":
                    r.append(Chipset.Arcadia)
                else:
                    r.append(Chipset.Unknown)
            return r

        def add_players(p: str):
            min_p = 0
            max_p = 0

            if ", " in p:
                min_max, sim = p.split(", ")
            else:
                min_max = p
                sim = None

            if " to " in min_max:
                min_p, max_p = min_max.split(" to ")
            elif " or " in min_max:
                min_p, max_p = min_max.split(" or ")
            elif " Only" in min_max:
                min_p = min_max.replace(" Only", "")
                max_p = min_p

            sim_p = True if sim is not None else False

            return int(min_p), int(max_p), sim_p

        self.name = tmp.get_string("name")
        if len(tmp.get_list("release_year_publisher")) == 2:
            self.release_year = tmp.get_datetime("release_year_publisher", "%Y", idx=0)
            self.publisher = Publisher(tmp.get_string("release_year_publisher", idx=1))
        else:
            self.release_year = datetime.min
            self.publisher = Publisher(tmp.get_string("release_year_publisher"))
        self.copyright = Publisher(tmp.get_string("copyright"))
        self.developer = tmp.get_string("developer")
        self.dev_team = []
        self.dev_team += add_people(tmp.get_list("dev_coder"), "Coder")
        self.dev_team += add_people(tmp.get_list("dev_design"), "Designer")
        self.dev_team += add_people(tmp.get_list("dev_graphics"), "Graphics")
        self.dev_team += add_people(tmp.get_list("dev_musician"), "Musician")
        self.dev_team += add_people(tmp.get_list("dev_sound_effects"), "Sound Effects")
        self.chipsets = add_chipsets(tmp.get_list("hardware"))
        self.genre = tmp.get_string("genre")
        self.license = tmp.get_string("license")
        self.languages = tmp.get_list("language")
        self.min_players, self.max_players, self.simultaneous_players = add_players(tmp.get_string("players"))
        self.lemon_score = tmp.get_string("lemon_score")
        self.lemon_votes = tmp.get_int("lemon_score_votes")

    @property
    def igame_name(self):
        def chipset():
            r = []
            for x in self.chipsets:
                r.append(x.name)
            return f"[{'/'.join(r)}]" if len(r) > 0 else ""

        def made_by():
            r = self.developer
            if r == "" or r == "Unknown":
                if self.copyright.name != "":
                    r = self.copyright.name
                elif self.publisher.name != "":
                    r = self.publisher.name
            return f"- {r}" if r != "" else ""

        return f"{self.name} {chipset()} {made_by()}".strip()

    @property
    def igame_genre(self) -> str:
        return f"{self.genre}"
