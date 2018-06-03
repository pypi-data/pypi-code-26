import itertools
import os
import shutil
import tempfile
from datetime import datetime
from operator import attrgetter
from typing import BinaryIO, Iterable

import click
# noinspection PyPackageRequirements
import progressbar
from lhafile import LhaFile, BadLhafile

from igamelister.amiga.slave import Slave
from igamelister.cli.dataset import DataSet
from igamelister.table.align import Align
from igamelister.table.column import Column
from igamelister.table.header import Header
from igamelister.table.section import Section
from igamelister.table.table import Table
from igamelister.text_helpers import repeat, truncate, pad


class Slaves(DataSet):

    DATA_FILE = "slaves.dat"

    def __init__(self, config):
        super().__init__(config)

    def load(self, readonly: bool = False):
        try:
            self.data = self._load_data(Slaves.DATA_FILE)
            self.next_id = itertools.count(max([x.id for x in self.data]) + 1)
            DataSet.logger.info(f"Loaded iGameLister WHDLoad Slave data file (slaves.dat).")
        except ValueError:
            if readonly:
                DataSet.logger.error(f"iGameLister WHDLoad Slave data file (slaves.dat) not found.")
            else:
                DataSet.logger.info(f"iGameLister WHDLoad Slave data file (slaves.dat) not found. "
                                    f"Starting new data file.")

    def save(self):
        self._save_data(Slaves.DATA_FILE, self.data)

    #
    # Click command methods
    #

    def cli_slaves_add_path(self, source_root_path: str, installed_root_path: str, recursive_flag: bool):
        abs_source_root_path = os.path.abspath(source_root_path)

        supported_extensions = [".slave", ".lha"]

        if recursive_flag:
            file_list = list(self._walk_path(abs_source_root_path, supported_extensions, True))
        else:
            file_list = list(self._walk_path(abs_source_root_path, supported_extensions, False))

        file_count = len(file_list)

        if shutil.get_terminal_size().columns >= 120:
            bar_file_width = 35
            bar_file_format = progressbar.FormatCustomText("%(bar_file)s", {"bar_file": repeat(" ", bar_file_width)})
            bar_widgets = [
                progressbar.Percentage(),
                " ", progressbar.Bar(left="[", right="]", fill="."),
                " ", progressbar.Counter("%(value)5d"), f"/{file_count:d}",
                " | ", progressbar.Timer(format="Elapsed: %(elapsed)s"),
                " | ", bar_file_format, " "
            ]
        else:
            bar_file_width = 20
            bar_file_format = progressbar.FormatCustomText("%(bar_file)s", {"bar_file": repeat(" ", bar_file_width)})
            bar_widgets = [
                progressbar.Percentage(),
                " ", progressbar.Bar(left="[", right="]", fill="."),
                " ", progressbar.Timer(format="%(elapsed)s"),
                " | ", bar_file_format, " "
            ]
        bar = progressbar.ProgressBar(widgets=bar_widgets)

        for i in bar(range(file_count)):
            file_path = file_list[i]
            bar_file = pad(truncate(os.path.basename(file_path), bar_file_width), bar_file_width, Align.Left.value)
            bar_file_format.update_mapping(bar_file=bar_file)
            file_ext = os.path.splitext(file_path)[1].lower()
            if file_ext == ".slave":
                self._cli_slaves_add_slave(click.open_file(file_path, mode="rb"), installed_root_path)
            elif file_ext == ".lha":
                self._cli_slaves_add_archive(click.open_file(file_path, mode="rb"),
                                             abs_source_root_path,
                                             installed_root_path)

    def cli_slaves_add_slave(self, source_file: BinaryIO, installed_root_path: str):
        self._cli_slaves_add_slave(source_file, installed_root_path)

    def cli_slaves_add_archive(self, source_file: BinaryIO, installed_root_path: str):
        self._cli_slaves_add_archive(source_file, source_file.name, installed_root_path)

    def cli_slaves_list(self, sort_by: str):
        self._cli_slaves_list(sort_by=sort_by)

    def cli_slaves_find(self, filter_text: str, sort_by: str):
        self._cli_slaves_list(filter_text, sort_by)

    def cli_slaves_details(self, slave_id: int):
        self._cli_slaves_details(slave_id=slave_id)

    def cli_slaves_remove(self, slave_id: int):
        self._cli_slaves_remove(slave_id=slave_id)

    #
    # Private methods
    #

    def _cli_slaves_details(self, slave_id: int = None):
        labels = []
        details = []

        def add(label, value):
            labels.append(label)
            details.append(value)

        matches = [x for x in self.data if x.id == slave_id]
        if len(matches) == 1:
            slave = matches[0]
        elif len(matches) > 1:
            raise ValueError(f"Multiple matches found for ID {slave_id}.")
        else:
            slave = None

        def get_details():
            add("ID", slave.id)
            add("Install path", slave.installed_path)
            add("File name", slave.file_name)
            add("File date", slave.file_datetime.strftime("%Y-%m-%d"))
            add("File size_bytes", slave.file_size)
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
            add("Kick. size_bytes", value)

            if slave.version < 17:
                return

            add("Slave Config", slave.configuration)

        if slave is not None:
            get_details()
            table = Table()
            section = Section()
            section.add(Header(f"Showing details for Slave '{slave.file_name}' (ID {slave.id}).", align=Align.Center))

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
            table.draw()
        else:
            click.echo("No matching WHDLoad Slave found in WHDLoad Slave data file.")

    def _cli_slaves_list(self, filter_text: str = None, sort_by: str = None):
        table = Table()

        title_str = "List of all WHDLoad Slaves in iGameLister WHDLoad Slave data file."
        if filter_text is not None:
            title_str += f" containing '{filter_text}'"
        title_str += ", sorted by "

        if sort_by is None or sort_by == "id":
            sort_attr = "id"
            title_str += "ID"
        elif sort_by == "file":
            sort_attr = "file_name"
            title_str += "file name"
        elif sort_by == "date":
            sort_attr = "file_datetime"
            title_str += "file date"
        elif sort_by == "dir":
            sort_attr = "installed_dir"
            title_str += "installed directory"
        elif sort_by == "name":
            sort_attr = "name"
            title_str += "name"

        title_str += "."

        section = Section()
        section.add(Header(title_str, align=Align.Center))

        def column_text(source):
            sort_key = attrgetter(sort_attr)
            if sort_attr == "id" or sort_attr == "file_datetime":
                sorted_data = sorted(self.data, key=lambda slv: sort_key(slv))
            else:
                sorted_data = sorted(self.data, key=lambda slv: sort_key(slv).lower())

            for slave in sorted_data:
                if filter_text is not None:
                    if filter_text.lower() not in slave.installed_path.lower():
                        continue

                def slave_name():
                    if slave.name is not None:
                        return slave.name.split("\n")
                    else:
                        return [""]

                if source == "id":
                    for i in range(len(slave_name())):
                        if i > 0:
                            yield ""
                        else:
                            yield slave.id
                elif source == "file_name":
                    for i in range(len(slave_name())):
                        if i > 0:
                            yield ""
                        else:
                            yield slave.file_name
                elif source == "installed_dir":
                    for i in range(len(slave_name())):
                        if i > 0:
                            yield ""
                        else:
                            yield slave.installed_dir
                elif source == "name":
                    for name in slave_name():
                        yield name
                elif source == "file_datetime":
                    for i in range(len(slave_name())):
                        if i > 0:
                            yield ""
                        else:
                            yield slave.file_datetime.strftime("%Y-%m-%d")
                else:
                    raise ValueError(f"Unhandled source '{source}'.")

        if shutil.get_terminal_size().columns >= 120:
            section.add(Column(column_text("id"), width=5, align=Align.Right, label="ID"))
            section.add(Column(column_text("file_datetime"), width=10, label="File date"))
            section.add(Column(column_text("installed_dir"), label="Installed directory"))
            section.add(Column(column_text("file_name"), width=40.0, label="File name"))
        else:
            section.add(Column(column_text("id"), width=5, align=Align.Right, label="ID"))
            section.add(Column(column_text("file_datetime"), width=10, label="File date"))
            section.add(Column(column_text("file_name"), width=30, label="File name"))
            section.add(Column(column_text("name"), label="Slave name"))
        table.add(section)
        table.draw()

    def _cli_slaves_remove(self, slave_id: int = None):
        match_index = None
        for i in range(len(self.data)):
            if slave_id == self.data[i].id:
                match_index = i
                file_name = self.data[i].file_name
                break

        if match_index is not None:
            del self.data[match_index]
            self.save()
            DataSet.logger.info(f"Removed WHDLoad Slave '{file_name}' with ID {slave_id}.")
        else:
            DataSet.logger.info(f"No match found for ID {slave_id} in WHDLoad Slave data file.")

    def _cli_slaves_add_slave(self, source_file: BinaryIO, installed_root_path: str):
        file_path = source_file.name
        file_name = os.path.basename(file_path)

        slave_path = self._reformat_amiga_path(installed_root_path, file_name)
        self._add_slave(source_file, installed_path=slave_path)

    def _cli_slaves_add_archive(self, source_file: BinaryIO, source_root_path: str, installed_root_path: str):
        file_path = source_file.name
        file_dir = os.path.dirname(file_path)
        file_name = os.path.basename(file_path)
        file_ext = os.path.splitext(file_name)[1].lower()

        if file_ext == ".lha":
            lha_file = None
            try:
                lha_file = LhaFile(source_file)
            except BadLhafile:
                DataSet.logger.error(f"Unable to open LHA file '{file_name}'. Skipping.")

            if lha_file is not None:
                archived_files = [x for x in lha_file.infolist()]
                for archived_file in archived_files:
                    archived_file_path = archived_file.filename
                    archived_file_name = os.path.basename(archived_file_path)
                    archived_file_ext = os.path.splitext(archived_file_path)[1].lower()
                    archived_file_dir = archived_file.directory
                    archived_file_datetime = archived_file.date_time
                    if archived_file_ext == ".slave":
                        with tempfile.TemporaryDirectory() as temp_dir:
                            extracted_dir = None
                            try:
                                extracted_dir = os.path.join(temp_dir, archived_file_dir)
                            except TypeError:
                                DataSet.logger.error(f"Unable to extract archive '{file_name}'. Skipping.")

                            if extracted_dir is not None:
                                extracted_file_path = os.path.join(extracted_dir, archived_file_name)
                                os.makedirs(extracted_dir)
                                open(extracted_file_path, "wb").write(lha_file.read(archived_file_path))
                                with open(extracted_file_path, "rb") as temp_file:
                                    installed_dir = file_dir.replace(source_root_path, "")
                                    installed_path = self._reformat_amiga_path(installed_root_path,
                                                                               f"{installed_dir}/{archived_file_path}")
                                    self._add_slave(temp_file,
                                                    file_datetime=archived_file_datetime,
                                                    installed_path=installed_path)
                                slave = self._get_slave_by_file_path(extracted_file_path)
                                if slave is not None:
                                    fake_file_path = os.path.join(file_dir, archived_file_path)
                                    slave.file_path = fake_file_path
                                    slave.file_datetime = archived_file_datetime
                                    self.save()
        else:
            DataSet.logger.error(f"Unsupported file '{file_name}'.")

    def _get_slave_by_file_path(self, file_path):
        for slave in self.data:
            if slave.file_path == file_path:
                return slave

    def _add_slave(self, slave_file: BinaryIO, installed_path: str, file_datetime: datetime = datetime.max):
        """Add a local WHDLoad slave file to the 'slaves_data' list.

        :param slave_file: A binary stream for a WHDLoad slave file.
        :param installed_path: The installed Slave path
        :param file_datetime: The file datetime. (optional)
        """
        match = False
        file_name = os.path.basename(slave_file.name)
        file_size = os.stat(slave_file.name).st_size
        if file_datetime == datetime.max:
            file_datetime = datetime.fromtimestamp(os.stat(slave_file.name).st_mtime)

        match_index = None
        for i in range(len(self.data)):
            if installed_path is not None:
                if installed_path == self.data[i].installed_path:
                    DataSet.logger.info(f"Duplicate match for '{file_name}' found in WHDLoad Slave data file.")
                    if file_size != self.data[i].file_size:
                        DataSet.logger.info(f"File size_bytes for '{file_name}' differs to existing record.")
                        match_index = i
                        break
                    if file_datetime.year != self.data[i].file_datetime.year \
                            or file_datetime.month != self.data[i].file_datetime.month \
                            or file_datetime.day != self.data[i].file_datetime.day:
                        DataSet.logger.info(f"File date for '{file_name}' differs to existing record.")
                        match_index = i
                        break
                    break

        if match_index is not None:
            del self.data[match_index]
            DataSet.logger.info(f"Removed '{file_name}' from WHDLoad Slave data file.")

        for item in self.data:
            if file_name == item.file_name:
                match = True
                break

        if not match:
            try:
                self.data.append(Slave.from_file(slave_file, installed_path, next(self.next_id)))
                self.save()
            except OSError as e:
                DataSet.logger.error(f"{e.args[0]} Skipping.")
            DataSet.logger.info(f"Added '{file_name}' to WHDLoad Slave data file.")

    @staticmethod
    def _reformat_amiga_path(amiga_path: str, file_path: str) -> str:
        file_path = file_path.replace("\\", "/")
        if amiga_path.endswith(":"):
            if file_path.startswith("/"):
                combined_path = f"{amiga_path}{file_path[1:]}"
            else:
                combined_path = f"{amiga_path}{file_path}"
        else:
            combined_path = f"{amiga_path}/{file_path}"
        combined_split = [x for x in combined_path.split("/") if x != ""]
        result = "/".join(combined_split)
        return result

    @staticmethod
    def _walk_path(path: str, supported_extensions: list, recursive: bool = False) -> Iterable:
        if recursive:
            for root_dir, dir_list, file_list in os.walk(path):
                for file_name in file_list:
                    if os.path.splitext(file_name)[1] in supported_extensions:
                        yield os.path.abspath(os.path.join(root_dir, file_name))
        else:
            root_dir, dir_list, file_list = next(os.walk(path))
            for file_name in file_list:
                if os.path.splitext(file_name)[1] in supported_extensions:
                    yield os.path.abspath(os.path.join(root_dir, file_name))
