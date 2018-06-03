import itertools
import shutil
from datetime import datetime

import click
# noinspection PyPackageRequirements
import progressbar
from requests import HTTPError

from igamelister.amiga.info.ada import ADA
from igamelister.amiga.info.bitworld import BitWorld
from igamelister.amiga.info.halloflight import HallOfLight
from igamelister.amiga.info.lemonamiga import LemonAmiga
from igamelister.amiga.info.pouet import Pouet
from igamelister.amiga.info.source import Source
from igamelister.amiga.package import Package
from igamelister.amiga.slave import Slave
from igamelister.cli.dataset import DataSet
from igamelister.table.align import Align
from igamelister.table.column import Column
from igamelister.table.header import Header
from igamelister.table.section import Section
from igamelister.table.table import Table
from igamelister.text_helpers import repeat, truncate, pad
from igamelister.webscraper.template import Template


class Packages(DataSet):

    DATA_FILE = "packages.dat"

    def __init__(self, config):
        super().__init__(config)

    def load(self, readonly: bool = False):
        try:
            self.data = self._load_data(Packages.DATA_FILE)
            self.next_id = itertools.count(max([x.id for x in self.data]) + 1)
            DataSet.logger.info(f"Loaded iGameLister WHDLoad Package data file (packages.dat).")
        except ValueError:
            if readonly:
                DataSet.logger.error(f"iGameLister WHDLoad Package data file (packages.dat) not found.")
            else:
                DataSet.logger.info(f"iGameLister WHDLoad Package data file (packages.dat) not found. "
                                    f"Starting new data file.")

    def save(self):
        self._save_data(Packages.DATA_FILE, self.data)

    #
    # Click command methods
    #

    def cli_packages_add_package(self, page_url: str):
        self._cli_packages_add_package(page_url)

    def cli_packages_add_all(self):
        self._cli_packages_add_category("all")

    def cli_packages_add_category(self, category: str):
        self._cli_packages_add_category(category)

    def cli_packages_list(self, sort_by: str):
        self._cli_packages_list(sort_by=sort_by)

    def cli_packages_find(self, filter_text: str, sort_by: str):
        self._cli_packages_list(filter_text, sort_by)

    def cli_packages_details(self, package_id: int):
        self._cli_packages_details(package_id)

    def cli_packages_remove(self, package_id: int):
        self._cli_packages_remove(package_id)

    #
    # Private methods
    #

    def _cli_packages_list(self, filter_text: str = None, sort_by: str = None):
        table = Table()
        section = Section()
        section.add(Header("List of all packages in iGameLister WHDLoad Package data file."))

        def get(col: str) -> str:
            for package in self.data:
                if col == "id":
                    yield package.id
                if col == "name":
                    yield package.name

        section.add(Column(get("id"), width=5, label="ID", align=Align.Right))
        section.add(Column(get("name"), label="Package name"))
        table.add(section)
        table.draw()

    def _cli_packages_details(self, package_id: int = None):
        labels = []
        details = []

        def add(label, value):
            labels.append(label)
            details.append(value)

        matches = [x for x in self.data if x.id == package_id]
        if len(matches) == 1:
            package = matches[0]
        elif len(matches) > 1:
            raise ValueError(f"Multiple matches found for ID {package_id}.")
        else:
            package = None

        def get_details():
            add("ID", package.id)
            add("Category", package.category.name)
            add("Release date", package.release_date.strftime("%Y-%m-%d"))

            try:
                value = f"{package.size_bytes / 1024:.2f} KiB"
            except ZeroDivisionError:
                value = f"{package.size_bytes} Bytes"
            add("Package size", value)

        if package is not None:
            get_details()
            table = Table()

            section = Section()
            section.add(Header(f"Details for Package '{package.name}' (ID {package.id}).",
                               align=Align.Center))

            def column_text(source):
                for i in range(len(labels)):

                    if source == "label":
                        if type(details[i]) is str:
                            for j in range(len(details[i].split("\n"))):
                                if j > 0:
                                    yield ""
                                else:
                                    yield labels[i]
                        else:
                            yield labels[i]

                    elif source == "details":
                        if type(details[i]) is str:
                            for line in details[i].split("\n"):
                                yield line
                        else:
                            yield details[i]

            section.add(Column(column_text("label"), width=14, align=Align.Right))
            section.add(Column(column_text("details")))
            table.add(section)

            for slave in package.slaves:
                self._package_slave_details(slave, table)

            for info in package.info:
                self._package_info(info, table)

            table.draw()

        else:
            click.echo("No matching WHDLoad Slave found in iGameLister WHDLoad Slave data file.")

    @staticmethod
    def _package_slave_details(slave: Slave, table: Table):
        labels = []
        details = []

        def add(label, value):
            labels.append(label)
            details.append(value)

        def get_details():
            add("File date", slave.file_datetime.strftime("%Y-%m-%d"))

            if slave.file_size < 1000:
                value = f"{slave.file_size} Bytes"
            else:
                try:
                    value = f"{slave.file_size / 1024} KiB"
                except ZeroDivisionError:
                    value = f"{slave.file_size} Bytes"
            add("File size", value)
            add("Version", slave.version)
            add("Flags", ', '.join([str(x) for x in slave.flags]))

            try:
                value = f"{slave.base_mem_size / 1024} KiB"
            except ZeroDivisionError:
                value = f"{slave.base_mem_size} Bytes"
            add("Chip mem", value)

            if slave.version < 8:
                return

            try:
                value = f"{slave.exp_mem / 1024} KiB"
            except ZeroDivisionError:
                value = f"{slave.exp_mem} Bytes"
            add("Exp. mem", value)

            if slave.version < 10:
                return

            add("Name", slave.name)
            add("Copyright", slave.copy)
            add("Info", slave.info)

            if slave.version < 16:
                return

            add("Kickstarts", ", ".join([str(x) for x in slave.kickstarts]))
            try:
                value = f"{slave.kickstart_size / 1024} KiB"
            except ZeroDivisionError:
                value = f"{slave.kickstart_size} Bytes"
            add("Kick. size", value)

            if slave.version < 17:
                return

            add("Slave Config", slave.configuration)

        get_details()
        section = Section()
        section.add(Header(f"Details for Slave '{slave.file_name}'."))

        def column_text(source):
            for i in range(len(labels)):

                if source == "label":
                    if type(details[i]) is str:
                        for j in range(len(details[i].split("\n"))):
                            if j > 0:
                                yield ""
                            else:
                                yield labels[i]
                    else:
                        yield labels[i]

                elif source == "details":
                    if type(details[i]) is str:
                        for line in details[i].split("\n"):
                            yield line
                    else:
                        yield details[i]

        section.add(Column(column_text("label"), width=14, align=Align.Right))
        section.add(Column(column_text("details")))
        table.add(section)

    @staticmethod
    def _package_info(info, table: Table):
        info_source = None
        if type(info) == HallOfLight:
            info_source = Source.HoL
        elif type(info) == LemonAmiga:
            info_source = Source.Lemon
        elif type(info) == ADA:
            info_source = Source.ADA
        elif type(info) == BitWorld:
            info_source = Source.BitWorld
        elif type(info) == Pouet:
            info_source = Source.Pouet

        labels = []
        details = []

        def add(label, value):
            labels.append(label)
            details.append(value)

        def get_details():
            add("Name", info.igame_name)
            add("Genre", info.igame_genre)

        get_details()
        section = Section()

        chipsets = [x.name for x in info.chipsets]
        if len(chipsets) > 1:
            chipset_text = "chipsets"
        else:
            chipset_text = "chipset"

        section.add(Header(f"iGame information from {info_source.value} for {chipset_text}: {', '.join(chipsets)}."))

        def column_text(source):
            for i in range(len(labels)):

                if source == "label":
                    if type(details[i]) is str:
                        for j in range(len(details[i].split("\n"))):
                            if j > 0:
                                yield ""
                            else:
                                yield labels[i]
                    else:
                        yield labels[i]

                elif source == "details":
                    if type(details[i]) is str:
                        for line in details[i].split("\n"):
                            yield line
                    else:
                        yield details[i]

        section.add(Column(column_text("label"), width=14, align=Align.Right))
        section.add(Column(column_text("details")))
        table.add(section)

    def _add_package(self, package: tuple):
        try:
            self.data.append(Package(package, next(self.next_id)))
        except HTTPError:
            return

    @staticmethod
    def _get_package_list(category: str, show_count: bool) -> set:
        def get_packages(ini_file, url_path, section_name):
            x = set()
            tmp = Template(ini_file)
            for j in range(tmp.get_int("count")):
                x.add((tmp.get_string("name", idx=j),
                       url_path + tmp.get_string("url", idx=j),
                       tmp.get_int("size_bytes", idx=j),
                       datetime.strptime(tmp.get_string("date", idx=j), "%Y-%m-%d")))

            if show_count:
                Packages.logger.info(f"Got {len(x)} {section_name} packages.")
            return x

        r = set()
        if category == "all":
            r.update(get_packages("whdload_apps.ini", "apps/", "Application"))
            r.update(get_packages("whdload_cracktros.ini", "ctros/", "Cracktro"))
            r.update(get_packages("whdload_demos.ini", "demos/", "Demo"))
            r.update(get_packages("whdload_games.ini", "games/", "Game"))
            r.update(get_packages("whdload_mags.ini", "mags/", "Magazine"))
        elif category == "apps":
            r.update(get_packages("whdload_apps.ini", "apps/", "Application"))
        elif category in ["cracktros", "ctros"]:
            r.update(get_packages("whdload_cracktros.ini", "ctros/", "Cracktro"))
        elif category == "demos":
            r.update(get_packages("whdload_demos.ini", "demos/", "Demo"))
        elif category == "games":
            r.update(get_packages("whdload_games.ini", "games/", "Game"))
        elif category in ["magazines", "mags"]:
            r.update(get_packages("whdload_mags.ini", "mags/", "Magazine"))
        return r

    def _cli_packages_add_package(self, url: str):
        def validate_url(x: str) -> str:
            if x.startswith("http://"):
                x = x.replace("http://", "")
            elif x.startswith("https://"):
                x = x.replace("https://", "")

            if x.startswith("www.whdload.de"):
                x = x.replace("www.whdload.de", "")
            elif x.startswith("whdload.de"):
                x = x.replace("whdload.de", "")

            if x.startswith("/"):
                x = x[1:]

            return x

        package_url = validate_url(url)
        category = package_url.split("/")[0]
        all_packages = self._get_package_list(category, False)
        new_package = None
        for p in all_packages:
            if package_url == p[1]:
                new_package = p
                break
        if new_package is None:
            Packages.logger.info(f"No matching WHDLoad Package found.")
            return
        else:
            is_dupe = False
            for p in self.data:
                if new_package == p.list_info:
                    Packages.logger.info(f"Package '{new_package[0]}' already exists in WHDLoad Package data file.")
                    is_dupe = True
                    break
            if not is_dupe:
                Packages.logger.info(f"Adding '{new_package[0]}' to WHDLoad Package data file.")
                self._add_package(new_package)
                self.save()

    def _cli_packages_remove(self, package_id: int):
        del_indexes = [i for i in range(len(self.data)) if package_id == self.data[i].id]
        if len(del_indexes) == 1:
            Packages.logger.info(f"Removing '{self.data[del_indexes[0]].name}' from WHDLoad Package data file.")
            del self.data[del_indexes[0]]
            self.save()
        else:
            Packages.logger.info(f"Package ID '{package_id}' not found in WHDLoad Package data file.")

    def _cli_packages_add_category(self, category: str):
        Packages.logger.info(f"Getting package info from www.whdload.de ...")

        all_packages = self._get_package_list(category, True)

        dupes = set(x for x in all_packages for y in self.data if x == y.list_info)
        changed = set(x for x in all_packages for y in self.data if x[1] == y.list_info[1] and x[3] != y.list_info[3])
        new_packages = sorted(all_packages.difference(dupes), key=lambda x: x[0])

        if len(dupes) > 0:
            if len(dupes) == 1:
                package_text = "package"
            else:
                package_text = "packages"
            Packages.logger.info(f"Skipping {len(dupes)} duplicate {package_text}.")

        if len(changed) > 0:
            del_indexes = [i for x in changed for i in range(len(self.data)) if x[1] == self.data[i].list_info[1]]
            for i in del_indexes:
                del self.data[i]

            if len(changed) == 1:
                package_text = "package"
            else:
                package_text = "packages"
            Packages.logger.info(f"Removed {len(changed)} outdated {package_text} from WHDLoad Package data file.")

        if len(new_packages) > 0:
            if len(new_packages) == 1:
                package_text = "package"
            else:
                package_text = "packages"
            Packages.logger.info(f"Adding {len(new_packages)} {package_text} to WHDLoad Package data file.")

            if shutil.get_terminal_size().columns >= 120:
                bar_name_width = 35
                bar_name_format = progressbar.FormatCustomText("%(bar_name)s",
                                                               {"bar_name": repeat(" ", bar_name_width)})
                bar_widgets = [
                    progressbar.Percentage(),
                    " ", progressbar.Bar(left="[", right="]", fill="."),
                    " ", progressbar.Counter("%(value)5d"), f"/{len(new_packages):d}",
                    " | ", progressbar.Timer(format="Elapsed: %(elapsed)s"),
                    " | ", bar_name_format, " "
                ]
            else:
                bar_name_width = 20
                bar_name_format = progressbar.FormatCustomText("%(bar_name)s",
                                                               {"bar_name": repeat(" ", bar_name_width)})
                bar_widgets = [
                    progressbar.Percentage(),
                    " ", progressbar.Bar(left="[", right="]", fill="."),
                    " ", progressbar.Timer(format="%(elapsed)s"),
                    " | ", bar_name_format, " "
                ]
            bar = progressbar.ProgressBar(widgets=bar_widgets, min_value=0, max_value=len(new_packages))

            bar_name = pad(truncate("Starting ...", bar_name_width), bar_name_width, Align.Left.value)
            bar_name_format.update_mapping(bar_name=bar_name)
            bar.update(bar.min_value)

            for i in range(len(new_packages)):
                name = new_packages[i][0]
                bar_name = pad(truncate(f"{name}", bar_name_width), bar_name_width, Align.Left.value)
                bar_name_format.update_mapping(bar_name=bar_name)
                DataSet.logger.info(f"Getting info for '{name}'")
                bar.update(i + 1)
                self._add_package(new_packages[i])
                self.save()
            bar_name = pad(truncate("Finished!", bar_name_width), bar_name_width, Align.Left.value)
            bar_name_format.update_mapping(bar_name=bar_name)
            DataSet.logger.info("Finished!")
            bar.update(bar.max_value)
        else:
            Packages.logger.info(f"No packages to add to WHDLoad Package data file.")
