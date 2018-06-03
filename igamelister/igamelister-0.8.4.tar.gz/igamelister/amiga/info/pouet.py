from igamelister.amiga.chipset import Chipset
from igamelister.amiga.person import Person
from igamelister.amiga.publisher import Publisher
from igamelister.webscraper.template import Template


class Pouet:
    def __init__(self, page_id: int):
        tmp = Template("pouet.ini", page_id=page_id)

        def add_chipsets(c: list) -> list:
            r = []
            for x in c:
                if x == "Amiga OCS/ECS":
                    r.append(Chipset.OCS)
                    r.append(Chipset.ECS)
                elif x == "Amiga AGA":
                    r.append(Chipset.AGA)
                else:
                    r.append(Chipset.Unknown)
            return r

        def add_group(g: list) -> list:
            r = []
            for x in g:
                r.append(Publisher(x))
            return r

        def add_people(p: list) -> list:
            r = []
            for x in p:
                if " [" in x:
                    person, roles = x.split(" [")
                    if roles.endswith("]"):
                        roles = roles[:-1]

                    for role in roles.split(", "):
                        r.append(Person(person, role.title()))
                else:
                    r.append(Person(x, "Unknown"))
            return r

        self.name = tmp.get_string("name")
        self.groups = add_group(tmp.get_list("group"))
        self.chipsets = add_chipsets(tmp.get_list("platform"))
        self.category = tmp.get_string("type").title()
        self.release_date_format = tmp.get_datetime_format("release_date", ["%Y", "%B %Y"])
        self.release_date = tmp.get_datetime("release_date", self.release_date_format)
        self.party = tmp.get_string("release_party")
        self.compo = tmp.get_string("party_compo").title()
        self.rank = tmp.get_int("compo_rank")
        self.dev_team = add_people(tmp.get_list("credits"))

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
