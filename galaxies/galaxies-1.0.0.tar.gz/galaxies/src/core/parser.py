# -*- coding: utf-8 -*-
""" Read a source database containing reuses in a corpus, then save the useful information into a SQLite3 database.

The source database is usually the one outputted by the text-align software (located at
https://github.com/ARTFL-Project/text-align), but any CSV file properly configured can be used.
"""

import codecs
import re
import json

from progressbar import ProgressBar, Percentage, Counter, Timer

import galaxies.src.core.database_tools as db
from galaxies.src.common.file import line_count

PB_WIDGETS = ["Processed: ", Counter(), " lines [", Percentage(), "], ",
              Timer()]


class UnknownFormatException(Exception):
    def __init__(self, database_source):
        super().__init__("The database {} is in an unknown or not supported format.".format(database_source))


def parse_reuse_file(database_source: str, database_target: str, max_book_to_add: int, delimiter: str, encoding: str,
                     header: bool, index_src_author: int, index_src_title: int, index_src_date: int,
                     index_src_text_matched: int, index_src_start_byte: int, index_src_end_byte: int,
                     index_target_author: int, index_target_title: int, index_target_date: int,
                     index_target_text_matched: int, index_target_start_byte: int, index_target_end_byte: int):
    """ Read a source database containing reuses in a corpus, then save the useful information into a SQLite3 database.

    The source database is usually the one outputted by the text-align software (located at
    https://github.com/ARTFL-Project/text-align), but any CSV file properly configured can be used.
    """
    if _is_sequence_of_json(database_source, encoding):
        _parse_json_file(database_source, database_target, encoding, header,
                         max_book_to_add)
    elif _is_csv(database_source, delimiter, encoding):
        _parse_csv_file(database_source, database_target, max_book_to_add,
                        delimiter, encoding, header, index_src_author,
                        index_src_title, index_src_date, index_src_text_matched,
                        index_src_start_byte, index_src_end_byte,
                        index_target_author, index_target_title,
                        index_target_date, index_target_text_matched,
                        index_target_start_byte, index_target_end_byte)
    else:
        raise UnknownFormatException(database_source)


def _parse_json_file(database_source: str, database_dest: str, encoding: str,
                     header: bool, max_book_to_add: int):
    """ Read a source database containing reuses in a corpus, then save the useful information into a SQLite3 database.
    The source database is usually the one outputted by the text-align software (located at
    https://github.com/ARTFL-Project/text-align), but any CSV file properly configured can be used.
    This function is called by `parse_reuse_file` and must be able to parse

    """
    # Set the number of lines to read for the progress bar
    if max_book_to_add < 0:
        max_book_to_add = line_count(database_source)

    connexion = db.connexion(database_dest)
    curseur = connexion.cursor()

    with codecs.open(database_source, 'r', encoding, errors='replace') as file:
        if header:
            # Remove the header
            file.readline()

        progress_bar = ProgressBar(widgets=PB_WIDGETS, maxval=max_book_to_add)
        progress_bar.start()

        for line_number, line in enumerate(file):
            if line_number == max_book_to_add:
                break

            l = json.loads(line.strip("\n"))

            # Add the two books into the database (do nothing if one of them is
            # already present).
            db.add_book(item('source_author', l),
                        item('source_title', l),
                        item_num('source_create_date', l),
                        curseur)
            db.add_book(item('target_author', l),
                        item('target_title', l),
                        item_num('target_create_date', l),
                        curseur)

            # Retrieve the identifier of the two books (because the two of them
            # may be already present).
            id_src = db.get_id_book(item('source_author', l),
                                    item('source_title', l),
                                    item_num('source_create_date', l),
                                    curseur)
            id_dest = db.get_id_book(item('target_author', l),
                                     item('target_title', l),
                                     item_num('target_create_date', l),
                                     curseur)

            # Add a reuse for the source book and the destination book
            real_id_book_source = db.id_ref(item('source_author', l),
                                            item('source_title', l),
                                            item_num('source_create_date', l))
            real_id_book_target = db.id_ref(item('target_author', l),
                                            item('target_title', l),
                                            item_num('target_create_date', l))
            db.add_reuse(id_src,
                         int(l['source_start_byte']),
                         int(l['source_end_byte']) - int(l['source_start_byte']),
                         l['source_passage'],
                         id_dest,
                         int(l['target_start_byte']),
                         int(l['target_end_byte']) - int(l['target_start_byte']),
                         l['target_passage'],
                         real_id_book_source,
                         real_id_book_target,
                         curseur)

            progress_bar.update(line_number + 1)

        progress_bar.finish()
        connexion.commit()
        connexion.close()


def _parse_csv_file(database_source: str, database_dest: str,
                    max_book_to_add: int, delimiter: str, encoding: str,
                    header: bool, index_src_author: int, index_src_title: int,
                    index_src_date: int, index_src_text_matched: int,
                    index_src_start_byte: int, index_src_end_byte: int,
                    index_dest_author: int, index_dest_title: int,
                    index_dest_date: int, index_dest_text_matched: int,
                    index_dest_start_byte: int, index_dest_end_byte: int):
    # Set the number of lines to read for the progress bar
    if max_book_to_add < 0:
        max_book_to_add = line_count(database_source)

    connexion = db.connexion(database_dest)
    curseur = connexion.cursor()
    with codecs.open(database_source, 'r', encoding, errors='replace') as file:
        if header:
            # Remove the header
            file.readline()

        progress_bar = ProgressBar(widgets=PB_WIDGETS, maxval=max_book_to_add)
        progress_bar.start()
        for line_number, line in enumerate(file):
            if line_number == max_book_to_add:
                break

            l = re.split(delimiter, line)

            # Add the two books into the database (do nothing if one of them is
            # already present).
            db.add_book(l[index_src_author],
                        l[index_src_title],
                        l[index_src_date], curseur)
            db.add_book(l[index_dest_author],
                        l[index_dest_title],
                        l[index_dest_date], curseur)

            # Retrieve the identifier of the two books (because the two of them
            # may be already present).
            id_src = db.get_id_book(l[index_src_author],
                                    l[index_src_title],
                                    l[index_src_date],
                                    curseur)
            id_dest = db.get_id_book(l[index_dest_author],
                                     l[index_dest_title],
                                     l[index_dest_date],
                                     curseur)

            # Add a reuse for the source book and the destination book
            real_id_book_source = db.id_ref(l[index_src_author], l[index_src_title], l[index_src_date])
            real_id_book_target = db.id_ref(l[index_dest_author], l[index_dest_title], l[index_dest_date])
            db.add_reuse(id_src,
                         int(l[index_src_start_byte]),
                         int(l[index_src_end_byte]) -
                         int(l[index_src_start_byte]),
                         l[index_src_text_matched],
                         id_dest,
                         int(l[index_dest_start_byte]),
                         int(l[index_dest_end_byte]) -
                         int(l[index_dest_start_byte]),
                         l[index_dest_text_matched],
                         real_id_book_source,
                         real_id_book_target,
                         curseur)
            progress_bar.update(line_number + 1)

    progress_bar.finish()
    connexion.commit()
    connexion.close()


def item(key, line):
    if key in line.keys():
        return line[key]
    else:
        return "Inconnu"


def item_num(key, line):
    if key in line.keys():
        return line[key]
    else:
        return 0


def clefs_fichier(file_path):
    FichierEntree = codecs.open(file_path, 'r', 'utf-8')
    L = json.loads(FichierEntree.readline()[0:-1])
    print(L.keys())


def presence_clef(Clef, Fic):
    FichierEntree = codecs.open(Fic, 'r', 'utf-8')
    L = FichierEntree.readline()
    nligne = 0
    liste_lignes = []
    while L != "":
        nligne += 1
        if not Clef in json.loads(L[0:-1]).keys():
            liste_lignes.append((nligne))
            print("Absence clef \'" + Clef + "\' sur ligne n°" + str(nligne))
        if nligne.__mod__(100000) == 0:
            print("\tNombre lignes explorées " + str(nligne))
        L = FichierEntree.readline()
    print(liste_lignes)
    FichierEntree.close()


def _is_sequence_of_json(file_path: str, encoding: str) -> bool:
    """ Check if the file is in the "sequence of JSON" format. """
    with open(file_path, encoding=encoding) as file:
        line = file.readline().strip("\n")
        return line[0] == "{" and line[-1] == "}"


def _is_csv(file_path: str, delimiter: str, encoding: str) -> bool:
    """ Check if the file is in the "CSV" format. """
    with open(file_path, encoding=encoding) as file:
        try:
            for line in file:
                re.split(delimiter, line)
                return True
        except Exception:
            return False


if __name__ == '__main__':
    pass
