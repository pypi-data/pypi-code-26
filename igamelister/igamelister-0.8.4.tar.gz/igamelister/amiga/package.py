from datetime import datetime

from igamelister.amiga.category import Category
from igamelister.amiga.info.ada import ADA
from igamelister.amiga.info.bitworld import BitWorld
from igamelister.amiga.info.halloflight import HallOfLight
from igamelister.amiga.info.lemonamiga import LemonAmiga
from igamelister.amiga.info.pouet import Pouet
from igamelister.amiga.info.source import Source
from igamelister.amiga.person import Person
from igamelister.amiga.slave import Slave
from igamelister.webscraper.template import Template


class Package:

    def __init__(self, package: tuple, package_id: int = None):
        if package_id is not None:
            self.id = package_id
        else:
            self.id = None

        self.list_info = package

        package_url = self.list_info[1]

        tmp = Template("whdload_package.ini", package_url=package_url)

        def add_category(rel_url: str) -> Category:
            cat = rel_url.split('/')[0]
            for x in Category:
                if cat == x.value:
                    return x

        def add_authors(p: list) -> list:
            r = []
            for x in p:
                r.append(Person(x, "WHDLoadPackage"))
            return r

        def add_slaves(slaves: list) -> list:
            r = []
            if len(slaves) == 0:
                return r

            table = slaves[0]
            d = {}

            def get(key: str) -> list:
                try:
                    return table.xpath(
                        f"./tr[td][position() > {slave_idx[i]} and not (position() >= {end_idx})]"
                        f"/td[text()='{key}']/following-sibling::td/text()")
                except IndexError:
                    return [""]

            def get_string(key: str, idx: int = None, sep: str = "\n") -> str:
                if idx is not None:
                    try:
                        return str(get(key)[idx])
                    except IndexError:
                        return ""
                else:
                    return sep.join(get(key))

            def get_int(key: str, idx: int = 0) -> int:
                try:
                    return int(get(key)[idx])
                except ValueError:
                    return 0

            def get_list(key: str, sep: str, idx: int = 0) -> list:
                s = get_string(key, idx)
                if len(s) > 0:
                    return s.split(sep)
                else:
                    return []

            def get_int_from_list(key: str, sep: str, idx: int) -> int:
                lst = get_list(key, sep, idx=0)
                if len(lst) > idx:
                    if len(lst[idx]) > 0:
                        return int(lst[idx])
                return 0

            slave_idx = []
            for i in range(int(table.xpath("count(./tr[td])"))):
                if table.xpath(f"./tr[{i}]/td[@colspan=2]"):
                    slave_idx.append(i - 1)

            for i in range(len(slave_idx)):
                if i == len(slave_idx) - 1:
                    end_idx = int(table.xpath("count(./tr[td])") + 1)
                else:
                    end_idx = slave_idx[i + 1]

                h = table.xpath(f"./tr[td][{slave_idx[i]}]/td")[0].text_content().split(" - ")
                d["file_name"] = h[0]
                d["file_datetime"] = datetime.strptime(h[1], "%d.%m.%Y %H:%M:%S")
                d["file_size_bytes"] = int(h[2].replace(" bytes", ""))

                d["slave_version"] = get_int("required WHDLoad version")
                d["slave_flags"] = get_list("flags", " ")
                d["slave_chip_mem"] = get_int_from_list("required Chip Memory", " ", 0) * 1024
                d["slave_exp_mem"] = get_int_from_list("Expansion Memory", " ", 0) * 1024
                if d["slave_exp_mem"] == 0:
                    d["slave_exp_mem"] = get_int_from_list("required Expansion Memory", " ", 0) * 1024
                d["slave_name"] = get_string("info name")
                d["slave_copy"] = get_string("info copy")
                d["slave_info"] = get_string("info install")
                d["slave_kickstart_names"] = get_list("Kickstart name", " ")
                d["slave_kickstart_size_bytes"] = get_int_from_list("Kickstart size", " ", 0) * 1024
                d["slave_kickstart_checksums"] = get_list("Kickstart checksum", " ")
                d["slave_configuration"] = get_string("Configuration")

                r.append(Slave.from_web(d))
            return r

        def add_info() -> list:
            r = []

            def add(source: Source):
                if source == Source.HoL:
                    for i in tmp.get_list("package_hol_links"):
                        r.append(HallOfLight(i))
                elif source == Source.Lemon:
                    for i in tmp.get_list("package_lemon_links"):
                        r.append(LemonAmiga(i))
                elif source == Source.ADA:
                    for i in tmp.get_list("package_ada_links"):
                        r.append(ADA(i))
                elif source == Source.BitWorld:
                    for i in tmp.get_list("package_bitworld_links"):
                        r.append(BitWorld(i))
                elif source == Source.Pouet:
                    for i in tmp.get_list("package_pouet_links"):
                        r.append(Pouet(i))

            if self.category == Category.Game:
                add(Source.HoL)
                add(Source.Lemon)
            elif self.category == Category.Demo:
                add(Source.ADA)
                add(Source.BitWorld)
                add(Source.Pouet)
            elif self.category == Category.Magazine:
                add(Source.ADA)
                add(Source.BitWorld)
                add(Source.Pouet)
            elif self.category == Category.Cracktro:
                add(Source.HoL)
                add(Source.Lemon)
                add(Source.ADA)
                add(Source.BitWorld)
                add(Source.Pouet)

            return r

        self.package_url = package_url
        self.category = add_category(self.package_url)

        self.name = tmp.get_string("package_name")
        self.release_date = tmp.get_datetime("package_release_date", "%Y-%m-%d")
        self.size_bytes = tmp.get_int("package_size_bytes")
        self.authors = add_authors(tmp.get_list("package_authors"))
        self.notes = tmp.get_string("package_notes")
        self.info = add_info()
        self.slaves = add_slaves(tmp.get("slave_table"))
