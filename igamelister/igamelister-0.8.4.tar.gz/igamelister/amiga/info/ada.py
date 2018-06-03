from datetime import datetime

from igamelister.amiga.chipset import Chipset
from igamelister.amiga.person import Person
from igamelister.amiga.publisher import Publisher
from igamelister.webscraper.template import Template


class ADA:
    def __init__(self, page_id: int):
        tmp = Template("ada.ini", page_id=page_id)

        details = tmp.get_list("details")

        sections = []
        for i in range(len(details)):
            if details[i].endswith(":"):
                sections.append((i + 1, details[i]))

        def get(idx: int):
            r = []
            for j in range(sections[idx][0], sections[idx + 1][0]):
                if details[j].endswith(":"):
                    break
                r.append(details[j])
            return r

        def get_string(key: str, idx: int = None, sep: str = ", ") -> str:
            for j in range(len(sections)):
                if sections[j][1] == key:
                    r = get(j)
                    if idx is not None:
                        return r[idx]
                    else:
                        return sep.join(r)
            return ""

        def get_list(key: str) -> list:
            for j in range(len(sections)):
                if sections[j][1] == key:
                    return get(j)
            return []

        def get_datetime(key: str, fmt: str) -> datetime:
            if fmt == '':
                return datetime.min

            s = get_string(key, idx=0)
            if s != '' or s != '-':
                return datetime.strptime(s, fmt)
            else:
                return datetime.min

        def get_datetime_format(key: str, fmt: list) -> str:
            s = get_string(key, idx=0)
            if s == '' or s == '-':
                return ''

            for f in fmt:
                try:
                    datetime.strptime(s, f)
                    return f
                except ValueError:
                    continue

        def add_people(names, role: str) -> list:
            r = []
            if type(names) == list:
                for name in names:
                    r.append(Person(name, role))
            elif type(names) == str:
                r.append(Person(names, role))
            return r

        def add_chipsets(c: list) -> list:
            r = []
            for x in c:
                if x == "Ocs":
                    r.append(Chipset.OCS)
                elif x == "Ecs":
                    r.append(Chipset.ECS)
                elif x == "Aga":
                    r.append(Chipset.AGA)
                else:
                    r.append(Chipset.Unknown)
            return r

        def add_groups(g: list) -> list:
            r = []
            for x in g:
                r.append(Publisher(x))
            return r

        def add_party(p: list) -> list:
            if len(p) > 0:
                party = p[0]
                if len(p) > 1:
                    compo = p[1].replace(" compo", "")
                    rank = p[2][8:-2]
                else:
                    compo = ""
                    rank = 0
            else:
                party = ""
                compo = ""
                rank = 0
            return [party, compo, rank]

        self.name = get_string("Demo:")
        self.groups = add_groups(get_list("Group:"))
        self.dev_team = add_people(get_list("Code:"), "Coder")
        self.dev_team += add_people(get_list("3D:"), "3D Modeller")
        self.dev_team += add_people(get_list("Raytracing:"), "Raytracing")
        self.dev_team += add_people(get_list("Support:"), "Support")
        self.dev_team += add_people(get_list("Graphics:"), "Graphics")
        self.dev_team += add_people(get_list("Music:"), "Musician")
        self.category = get_string("Category:")
        self.release_date_format = get_datetime_format("Release:", ["%Y", "%B %Y"])
        self.release_date = get_datetime("Release:", self.release_date_format)
        self.chipsets = add_chipsets(get_list("Chipset:"))
        self.party, self.compo, self.rank = add_party(get_list("Party:"))

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
