# -*- coding: utf-8 -*-
""" Ce module contient des fonctions gérant l'accès, la création et la
suppression dans la base de données SQLite3.
"""
import sqlite3
import os.path


DATABASE_NAME = "galaxie.db"

# Files containing SQLite3 statements
SQL_CREATION_GALAXIE = os.path.join(os.path.dirname(__file__),
                                    "../../res/sql/create_galaxie.sql")


def connexion(database_path: str) -> sqlite3.Connection:
    """ Effectue une connexion vers la base de données """
    return sqlite3.connect(database_path, 1, 0, 'EXCLUSIVE')


def create_database(database_path: str) -> None:
    with open(SQL_CREATION_GALAXIE) as file:
        statement = file.read()

    cursor = connexion(database_path).cursor()
    cursor.executescript(statement)
    cursor.close()


def add_book(auteur, titre, date, cursor):
    """ Ajoute un livre dans la base de données. """
    statement = """
        INSERT INTO livres values (?,?,?,?)
    """
    id_book = id_ref(auteur, titre, date)

    try:
        cursor.execute(statement, (id_book, auteur, titre, date))
    # Don't add books already in the database
    except sqlite3.IntegrityError:
        pass


def id_ref(auteur, titre, date):
    """ Retourne un ID formaté utilisé dans la base de données. """
    return auteur + titre + str(date)


def get_id_book(auteur, titre, date, cursor):
    """ Retourne l'ID d'un livre depuis la base de données. """
    query = """
        SELECT rowid
        FROM livres
        WHERE idLivre = (?)
    """
    cursor.execute(query, (id_ref(auteur, titre, date),))
    return cursor.fetchone()[0]


def add_reuse(id_source, coordonnee_source, empan_source, texte_source,
              id_cible, coordonnee_cible, empan_cible, texte_cible,
              real_id_book_source, real_id_book_target, cursor):
    """ Ajoute une réutilisation dans la base de données. """
    statement = '''
        INSERT INTO grapheReutilisations values (?,?,?,?,?,?,?,?,?,?)
    '''
    cursor.execute(statement, (id_source, coordonnee_source, empan_source,
                               texte_source, id_cible, coordonnee_cible,
                               empan_cible, texte_cible, real_id_book_source,
                               real_id_book_target))


def max_nodes(database_path):
    """ Recupère l'ID qui apparait dans le plus de noeuds. """
    query = '''
        SELECT *
        FROM maxNoeud
    '''

    curseur = connexion(database_path).cursor()
    curseur.execute(query)
    return curseur.fetchone()[0]


if __name__ == '__main__':
    pass
