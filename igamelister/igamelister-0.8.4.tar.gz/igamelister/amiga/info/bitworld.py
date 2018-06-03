from igamelister.amiga.chipset import Chipset
from igamelister.amiga.person import Person
from igamelister.amiga.publisher import Publisher
from igamelister.webscraper.template import Template


class BitWorld:
    def __init__(self, page_id: int):
        tmp = Template("bitworld.ini", page_id=page_id)

        def add_group(g: list) -> list:
            r = []
            for x in g:
                r.append(Publisher(x))
            return r

        def add_people(names, role: str) -> list:
            r = []
            if type(names) == list:
                for name in names:
                    r.append(Person(name, role))
            elif type(names) == str:
                r.append(Person(names, role))
            return r

        def add_chipsets(t: list) -> list:
            r = []
            for x in t:
                if x == "ECS Chipset":
                    r.append(Chipset.ECS)
                elif x == "OCS Chipset":
                    r.append(Chipset.OCS)
                elif x == "AGA Chipset required":
                    r.append(Chipset.AGA)
            if len(r) == 0:
                # r.append(Chipset.ECS)
                r.append(Chipset.OCS)
            return r

        self.name = tmp.get_string("name")
        self.release_date_format = tmp.get_datetime_format("release_date", ["%Y-%m-%d", "%Y-%m", "%Y"])
        self.release_date = tmp.get_datetime("release_date", self.release_date_format)
        self.party = tmp.get_string("release_party")
        self.compo = tmp.get_string("party_compo")
        self.compo_rank = tmp.get_int("compo_rank")
        self.category = tmp.get_string("category")
        self.groups = add_group(tmp.get_list("groups"))
        self.dev_team = add_people(tmp.get_list("dev_coder"), "Coder")
        self.dev_team += add_people(tmp.get_list("dev_graphics"), "Graphics")
        self.dev_team += add_people(tmp.get_list("dev_text"), "Text")
        self.dev_team += add_people(tmp.get_list("dev_music"), "Musician")
        self.chipsets = add_chipsets(tmp.get_list("tags"))

    @property
    def igame_name(self):
        def chipset():
            r = []
            for x in self.chipsets:
                r.append(x.name)
            return f"[{'/'.join(r)}]" if len(r) > 0 else ""

        def groups():
            r = []
            for x in self.groups:
                r.append(x.name)
            return f"- {' & '.join(r)}" if len(r) > 0 else ""

        return f"{self.name} {chipset()} {groups()}"

    @property
    def igame_genre(self) -> str:
        return f"{self.category}"
