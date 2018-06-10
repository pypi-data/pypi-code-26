# -*- coding: utf-8 -*-
""" This module defines the main interface used by the CLI and the GUI of the software.
All methods defined here must be callable from the outside of this module (as its their main purpose...).
"""

import time
import os

import galaxies.src.core.parser as parser
import galaxies.src.core.database_tools as database_tools
import galaxies.src.core.graphe_galaxies as graphe_galaxies
import galaxies.src.core.extraction_galaxies as extraction_galaxies
import galaxies.src.core.extraction_galaxies_new as extraction_galaxies_new
from galaxies.src.common.file import delete_existing_files, makedirs


MESSAGE_GALAXIES_DATABASE_SCHEMA_INITIALISED = "Galaxies' database schema initialisation time: {} sec."
MESSAGE_CREATION_SUCCESS = "Creation successfully completed."


def create_reuses_database(*, database_src: str, path_file_galaxies: str, path_file_list_galaxies: str,
                           path_file_adjacency_graph: str, path_file_adjacency_graph_transposed: str,
                           path_dir_target: str, max_book_to_add: int, delimiter: str, encoding_src: str,
                           remove_header: bool, index_src_author: int, index_src_title: int, index_src_date: int,
                           index_src_text_matched: int, index_src_start_byte: int, index_src_end_byte: int,
                           index_target_author: int, index_target_title: int, index_target_date: int,
                           index_target_text_matched: int, index_target_start_byte: int, index_target_end_byte: int):
    """ Create the SQLite3 database containing only the useful information the
    software needs to process the graph.
    :param database_src: The path to the database containing all the reuses'.
    This database must be in the TSV, TAB or CSV format.
    :param path_file_galaxies: The path to the SQLite3 which is gonna be created.
    :param path_file_list_galaxies: The path to the file containing the list of
    all galaxies.
    :param path_file_adjacency_graph: The path of the pickle file containing the
    adjacency graph.
    :param path_file_adjacency_graph_transposed: The path of the pickle file
    containing the transposed of the adjacency graph.
    :param path_dir_target: The directory containing all the files which'll be
    created by the software.
    :param max_book_to_add: The maximal number of books to add in the SQLite3
    database. If negative, all the books possible are added.
    :param delimiter: The delimiter of the source database containing all the
    reuses'.
    :param encoding_src: The encoding of the source database containing all the
    reuses'.
    :param remove_header: Remove the header present in the source database
    containing all the reuses'.
    :param index_src_author: The index in the source database matching a column
    containing the author of a source reuse.
    :param index_src_title: The index in the source database matching a column
    containing the title of a source reuse.
    :param index_src_date: The index in the source database matching a column
    containing the date of a source reuse.
    :param index_src_text_matched: The index in the source database matching a
    column containing the text matched of a source reuse.
    :param index_src_start_byte: The index in the source database matching a
    column containing the start byte of a source reuse.
    :param index_src_end_byte: The index in the source database matching a
    column containing the end byte of a source reuse.
    :param index_target_author: The index in the source database matching a column
    containing the author of a destination (or target) reuse.
    :param index_target_title: The index in the source database matching a column
    containing the title of a destination (or target) reuse.
    :param index_target_date: The index in the source database matching a column
    containing the date of a destination (or target) reuse.
    :param index_target_text_matched: The index in the source database matching a
    column containing the text matched of a destination (or target) reuse.
    :param index_target_start_byte: The index in the source database matching a
    column containing the start byte of a destination (or target) reuse.
    :param index_target_end_byte: The index in the source database matching a
    column containing the end byte of a destination (or target) reuse.
    """
    global MESSAGE_GALAXIES_DATABASE_SCHEMA_INITIALISED

    # TODO: Ajouter args
    import galaxies.src.core.environment as env
    format_graphe = env.format_graph
    path_file_graphe_galaxie = env.path_file_graphe_galaxie
    path_file_graphe_galaxie_amas = env.path_file_graphe_galaxie_amas

    # Delete all existing databases to prevent unwanted errors
    delete_existing_files(path_file_galaxies, path_file_list_galaxies, path_file_adjacency_graph,
                          path_file_adjacency_graph_transposed)

    # Create result dir if it doesn't exists
    makedirs(path_dir_target, path_file_graphe_galaxie, path_file_graphe_galaxie_amas, exist_ok=True)

    # Initialise the galaxies' database schema
    t1 = time.clock()
    database_tools.create_database(database_path=path_file_galaxies)
    t2 = time.clock()
    print(MESSAGE_GALAXIES_DATABASE_SCHEMA_INITIALISED.format(t2 - t1))

    # Inserting all books from the input file in the galaxies' database
    parser.parse_reuse_file(database_source=database_src,
                            database_target=path_file_galaxies,
                            max_book_to_add=max_book_to_add,
                            delimiter=delimiter,
                            encoding=encoding_src,
                            header=remove_header,
                            index_src_author=index_src_author,
                            index_src_title=index_src_title,
                            index_src_date=index_src_date,
                            index_src_text_matched=index_src_text_matched,
                            index_src_start_byte=index_src_start_byte,
                            index_src_end_byte=index_src_end_byte,
                            index_target_author=index_target_author,
                            index_target_title=index_target_title,
                            index_target_date=index_target_date,
                            index_target_text_matched=index_target_text_matched,
                            index_target_start_byte=index_target_start_byte,
                            index_target_end_byte=index_target_end_byte)

    maxNoeud = 0
    if not graphe_galaxies.graphe_construit(path_file_galaxies):
        maxNoeud = graphe_galaxies.construction_graphe(database_path=path_file_galaxies)

    if not extraction_galaxies.composantes_extraites(path_file_list_galaxies):
        if maxNoeud == 0:
            maxNoeud = database_tools.max_nodes(path_file_galaxies)
        extraction_galaxies.extraction_composantes_connexes_(path_file_galaxies=path_file_galaxies,
                                                             path_file_list_galaxies=path_file_list_galaxies,
                                                             max_noeud=maxNoeud)

    extraction_galaxies_new.sauve_graphe_galaxie(path_file_galaxies=path_file_galaxies,
                                                 path_file_list_galaxies=path_file_list_galaxies,
                                                 path_file_graphe_galaxie=path_file_graphe_galaxie,
                                                 format_graphe=format_graphe)
    print(MESSAGE_CREATION_SUCCESS)


# TODO: Supprimer toutes les methodes ci-dessous 
def impressionTexteGUI(n, p, path):
    path_list_galaxies = os.path.join(os.path.dirname(path), "list_galaxies")
    res = "Composante " + n + ":\n\n"
    q = int(p)
    L = extraction_galaxies.textes_galaxie(n, path, path_list_galaxies)
    while L != set() and (q > 0 or p == 0):
        E = L.pop()
        res += "- " + str(E) + "\n"
        q -= 1
    return res


def impressionTexteEtReferenceLongueurGUI(n, p, path):
    path_list_galaxies = os.path.join(os.path.dirname(path), "list_galaxies")
    q = int(p)
    L = sorted(extraction_galaxies.textes_et_references_galaxie(n, path, path_list_galaxies),
               key=lambda reference: len(reference[0]))

    res_reuti = ""
    res_auteur = ""
    res_titre = ""
    res_date = ""

    while L != [] and (q > 0 or p == 0):
        E = L.pop()
        res_reuti += " -  " + E[0] + '\t\n'
        res_auteur += E[1][0] + '\t\n'
        res_titre += E[1][1] + '\t\n'
        res_date += str(E[1][2]) + '\t\n'
        q -= 1
    return res_reuti, res_auteur, res_titre, res_date


def extractionComposantes():
    maxNoeud = database_tools.max_nodes()
    t1 = time.clock()
    extraction_galaxies.extraction_composantes_connexes_(maxNoeud)
    t2 = time.clock()
    print("Extraction time of connected components :", t2 - t1, "s.")


def impressionTexte(numero_composante, p):
    q = p
    L = extraction_galaxies.textes_galaxie(numero_composante)

    while L != set() and (q > 0 or p == 0):
        E = L.pop()
        print("- " + str(E))
        q -= 1


def impressionTexteLongueur(numero_composante, p):
    q = p
    L = sorted(extraction_galaxies.textes_galaxie(numero_composante),
               key=lambda reference: len(reference))

    while L != [] and (q > 0 or p == 0):
        E = L.pop()
        print("- " + str(E))
        q -= 1


def impressionTexteEtReferenceLongueur(numero_composante, p):
    q = p
    L = sorted(extraction_galaxies.textes_et_references_galaxie(numero_composante),
               key=lambda reference: len(reference[0]))

    while L != [] and (q > 0 or p == 0):
        E = L.pop()
        print("- " + str(E[0]) + " references: " + str(E[1]))
        q -= 1


def impressionTexteEtReference(numero_composante, p):
    q = p
    L = extraction_galaxies.textes_et_references_galaxie(numero_composante)

    while L != set() and (q > 0 or p == 0):
        E = L.pop()
        print("- " + str(E[0]) + " references: " + str(E[1]))
        q -= 1


def impressionTexteEtReferenceAnciennete(numero_composante, p):
    q = p
    L = sorted(extraction_galaxies.textes_et_references_galaxie(numero_composante),
               key=lambda reference: str(reference[1][2]))

    while L != [] and (q > 0 or p == 0):
        E = L[0]
        L = L[1:]
        print("- " + str(E[0]) + " references: " + str(E[1]))
        q -= 1


if __name__ == '__main__':
    pass
