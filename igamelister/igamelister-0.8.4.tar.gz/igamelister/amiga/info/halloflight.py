from igamelister.amiga.chipset import Chipset
from igamelister.amiga.person import Person
from igamelister.amiga.publisher import Publisher
from igamelister.webscraper.template import Template


class HallOfLight:
    def __init__(self, page_id: int):
        tmp = Template("halloflight.ini", page_id=page_id)

        def add_publishers(pubs: list) -> list:
            if pubs is not None:
                result = []
                for pub in pubs:
                    name_region = pub.split(" - ")
                    name = ""
                    region = ""
                    if len(name_region) == 2:
                        name = name_region[0]
                        region = name_region[1]
                    elif len(name_region) > 2:
                        for i in range(len(name_region) - 1):
                            name += name_region[i]
                            if i < len(name_region) - 2:
                                name += " - "
                        region = name_region[-1]
                    result.append(Publisher(name, region))
                return result
            return []

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
                elif x == "AmigaCD":
                    r.append(Chipset.AmigaCD)
                elif x == "Coin-Op - Arcadia":
                    r.append(Chipset.Arcadia)
                else:
                    r.append(Chipset.Unknown)
            return r

        def add_people(p: list) -> list:
            r = []
            for i in range(0, len(p), 2):
                role = p[i][:-2]
                name = p[i+1]
                r.append(Person(name, role))
            return r

        self.name = tmp.get_string("name")
        self.release_year = tmp.get_datetime("release_year", "%Y")
        self.publishers = add_publishers(tmp.get_list("publisher"))
        self.budget_publishers = add_publishers(tmp.get_list("budget_publisher"))
        self.license = tmp.get_string("license")
        self.max_players = tmp.get_int("max_players")
        self.simultaneous_players = tmp.get_int("simultaneous_players")
        self.languages = tmp.get_list("language")
        self.chipsets = add_chipsets(tmp.get_list("hardware"))
        self.developer = tmp.get_string("developer")
        self.dev_team = add_people(tmp.get_list("artists"))
        self.genre_category = tmp.get_string("genre_category")
        self.genre_subcategory = tmp.get_string("genre_subcategory")
        self.genre_dimension = tmp.get_string("genre_dimension")
        self.genre_scrolltype = tmp.get_string("genre_scrolltype")
        self.genre_themes = tmp.get_list("genre_theme")
        self.genre_viewpoint = tmp.get_string("genre_viewpoint")

    @property
    def igame_name(self) -> str:
        def chipset():
            r = []
            for x in self.chipsets:
                r.append(x.name)
            return f"[{'/'.join(r)}]" if len(r) > 0 else ""

        def made_by():
            r = self.developer
            if r == "" or r == "Unknown":
                if len(self.publishers) > 0:
                    r = self.publishers[0].name
                elif len(self.budget_publishers) > 0:
                    r = self.budget_publishers[0].name
            return f"- {r}" if r != "" else ""

        return f"{self.name} {chipset()} {made_by()}".strip()

    @property
    def igame_genre(self) -> str:
        return f"{self.genre_subcategory}"
