# -*- coding: utf-8 -*-

import shelve

import galaxies.src.core.extraction_galaxies as extraction_galaxies
import galaxies.src.core.database_tools as db

import networkx as nx
from progressbar import ProgressBar, Percentage, Counter, Timer

from galaxies.src.common.maths import is_int


PB_WIDGETS = ["Processed: ", Counter(), " galaxies [", Percentage(), "], ",
              Timer()]


def degre_galaxie(G, curseur):
    curseur.execute(""" SELECT degreGalaxie FROM degreGalaxies WHERE idGalaxie = (?) """, (G,))
    return curseur.fetchone()[0]


def sauve_graphe_galaxie(path_file_galaxies, path_file_list_galaxies,
                         path_file_graphe_galaxie, format_graphe):
    with shelve.open(path_file_list_galaxies) as dirGalaxies:
        # Progress-bar initialisation
        progress_bar = ProgressBar(widgets=PB_WIDGETS, maxval=len(dirGalaxies))
        progress_bar.start()

        for index_galaxy, num_galaxy in enumerate(dirGalaxies.keys()):
            if not is_int(num_galaxy):
                continue
            liste_noeuds = dirGalaxies[str(num_galaxy)]
            creer_graphe(liste_noeuds, path_file_galaxies,
                         path_file_graphe_galaxie.format(num_galaxy), format_graphe)

            progress_bar.update(index_galaxy)
        progress_bar.finish()


def sauve_graphe_amas(listeNoeuds, galaxie_numero, amas_numero,
                      path_file_galaxies, path_file_graphe_galaxie_amas, format_graphe):
    creer_graphe(listeNoeuds, path_file_galaxies,
                 path_file_graphe_galaxie_amas.format(galaxie_numero,
                                                     amas_numero), format_graphe)


def creer_graphe(liste_noeuds, path_file_galaxies, path_file_graphe_galaxie, format_graph):
    """
    :param liste_noeuds:
    :param path_file_galaxies:
    :param path_file_graphe_galaxie:
    :param format_graph: Le format du graphe extrait. Peut-être "gexf" ou "gml"
    :return:
    """
    with db.connexion(path_file_galaxies) as connexion:
        cursor = connexion.cursor()

        arcs_emergents, arcs_incidents = dict(), dict()
        # Fetch all the reuses where the node is a source or a target from.
        for node in liste_noeuds:
            cursor.execute("""SELECT idReutilisation FROM grapheGalaxiesCible WHERE idNoeud = (?)""", (node,))
            result = cursor.fetchall()
            if len(result) != 0:
                arcs_incidents[node] = [reuse[0] for reuse in result]
            cursor.execute("""SELECT idReutilisation FROM grapheGalaxiesSource WHERE idNoeud = (?)""", (node,))
            result = cursor.fetchall()
            if len(result) != 0:
                arcs_emergents[node] = [reuse[0] for reuse in result]

        # Compute the graph with all previously fetched reuses.
        graph = nx.Graph()
        for arc_emergent in arcs_emergents.keys():
            texte = ""
            l_arcs = []
            for R in arcs_emergents[arc_emergent]:
                cursor.execute("""SELECT texteSource, idRefSource, idRefCible, texteCible FROM grapheReutilisations WHERE rowid = (?)""", (str(R),))
                Ref = cursor.fetchall()[0]
                T = caracterisques_reference(str(Ref[1]), cursor)
                if len(str(Ref[0])) > len(texte):
                    texte = str(Ref[0])
                cursor.execute("""SELECT idNoeud FROM grapheGalaxiesCible WHERE idReutilisation = (?)""", (str(R),))
                arrive = cursor.fetchall()
                TCible = caracterisques_reference(Ref[2], cursor)

                if len(arrive) != 1:
                    print("\ERROR")
                l_arcs.append((arc_emergent, str(arrive[0][0])))
                graph.add_node(arrive[0][0], texte=Ref[3], longueurTexte=len(Ref[3]), auteur=TCible[0], titre=TCible[1], date=TCible[2])

            graph.add_node(arc_emergent, texte=texte, longueurTexte=len(texte), auteur=T[0], titre=T[1], date=T[2])
            graph.add_edges_from(l_arcs)

        for arc_incident in arcs_incidents.keys():
            texte = ""
            l_arcs = []
            for R in arcs_incidents[arc_incident]:
                cursor.execute(""" SELECT texteCible, idRefCible, idRefSource, texteSource FROM grapheReutilisations WHERE rowid = (?) """,
                            (str(R),))
                Ref = cursor.fetchall()[0]
                T= caracterisques_reference(Ref[1], cursor)
                if len(str(Ref[0])) > len(texte):
                    texte = str(Ref[0])
                cursor.execute(""" SELECT idNoeud FROM grapheGalaxiesSource WHERE idReutilisation = (?) """, (str(R),))
                vient = cursor.fetchall()
                TSource = caracterisques_reference(Ref[2], cursor)
                if len(vient) != 1:
                    print("\tErreur!!")
                l_arcs.append((str(vient[0][0]), arc_incident))
                graph.add_node(vient[0][0], texte=Ref[3], longueurTexte=len(Ref[3]), auteur=TSource[0], titre=TSource[1], date=TSource[2])

            graph.add_node(arc_incident, texte=texte, longueurTexte=len(texte), auteur=T[0], titre=T[1], date=T[2])
            graph.add_edges_from(l_arcs)

        if format_graph.lower() == "gexf":
            nx.write_gexf(graph, path_file_graphe_galaxie, encoding='utf-8', prettyprint=True, version='1.2draft')
        elif format_graph.lower() == "gml":
            nx.write_gml(graph, path_file_graphe_galaxie)
        else:
            raise NotImplementedError("This graph format is currently not available or doesn't exists")


#TODO: Remove this function when we fix the bug duplicating all the nodes
def remove_empty_nodes(graph, needed_attribute="texte"):
    """ Iterate through all the nodes in `graph` and return a new graph containing all the nonempty nodes. """
    new_graph = nx.Graph()
    for (p, data) in graph.nodes(data=True):
        try:
            data[needed_attribute]
            new_graph.add_node(p, **data)
        except KeyError:
            pass
    return new_graph


def caracterisques_reference(idRef, curseur):
    curseur.execute(""" SELECT auteur, titre, date FROM livres WHERE rowid = (?) """,
                    (idRef,))
    return curseur.fetchall()[0]


def presence_auteur_galaxie_liste_noeuds(auteur, listeNoeuds, path_file_galaxies):
    connexion = db.connexion(path_file_galaxies)
    curseur = connexion.cursor()

    reutilisations = set()
    for Noeud in listeNoeuds:
        curseur.execute(
            """ SELECT idReutilisation FROM grapheGalaxiesCible WHERE idNoeud = (?) """, (Noeud,))
        L = curseur.fetchall()
        if L != []:
            reutilisations.add(L[0][0])
        curseur.execute(
            """ SELECT idReutilisation FROM grapheGalaxiesSource WHERE idNoeud = (?) """, (Noeud,))
        L = curseur.fetchall()
        if L != []:
            reutilisations.add(L[0][0])
    for idReutilisation in reutilisations:
        curseur.execute(""" SELECT idRefSource FROM grapheReutilisations WHERE rowid = (?) """,
                        (str(idReutilisation),))
        t1 = curseur.fetchall()[0]
        curseur.execute(
            """ SELECT auteur FROM livres WHERE rowid = (?) """, (t1[0],))
        if auteur in str.lower(curseur.fetchall()[0][0]):
            return auteur
        curseur.execute(""" SELECT idRefCible FROM grapheReutilisations WHERE rowid = (?) """,
                        (str(idReutilisation),))
        t1 = curseur.fetchall()[0]
        curseur.execute(
            """ SELECT auteur FROM livres WHERE rowid = (?) """, (t1[0],))
        if auteur in str.lower(curseur.fetchall()[0][0]):
            return auteur
    connexion.close()
    return ()


def presence_liste_nom_auteur_galaxie_liste_noeuds(LAuteurs, listeNoeuds, path_file_galaxies):
    connexion = db.connexion(path_file_galaxies)
    curseur = connexion.cursor()

    reutilisations = set()
    for Noeud in listeNoeuds:
        curseur.execute(
            """ SELECT idReutilisation FROM grapheGalaxiesCible WHERE idNoeud = (?) """, (Noeud,))
        L = curseur.fetchall()
        if L != []:
            reutilisations.add(L[0][0])
        curseur.execute(
            """ SELECT idReutilisation FROM grapheGalaxiesSource WHERE idNoeud = (?) """, (Noeud,))
        L = curseur.fetchall()
        if L != []:
            reutilisations.add(L[0][0])
    for idReutilisation in reutilisations:
        curseur.execute(""" SELECT idRefSource FROM grapheReutilisations WHERE rowid = (?) """,
                        (str(idReutilisation),))
        t1 = curseur.fetchall()[0]
        curseur.execute(
            """ SELECT auteur FROM livres WHERE rowid = (?) """, (t1[0],))
        if tout_dans(LAuteurs, str.lower(curseur.fetchall()[0][0])):
            return LAuteurs
        curseur.execute(""" SELECT idRefCible FROM grapheReutilisations WHERE rowid = (?) """,
                        (str(idReutilisation),))
        t1 = curseur.fetchall()[0]
        curseur.execute(
            """ SELECT auteur FROM livres WHERE rowid = (?) """, (t1[0],))
        if tout_dans(LAuteurs, str.lower(curseur.fetchall()[0][0])):
            return LAuteurs
    connexion.close()
    return ()


def tout_dans(L, F):
    for X in L:
        if X not in F:
            return ()
    return L


def galaxies_auteur(Auteur, path_file_galaxies, path_file_list_galaxies):
    nomAuteur = str.lower(Auteur)
    dirGalaxies = shelve.open(path_file_list_galaxies)
    nbreGalaxies = dirGalaxies['nbreGalaxies']

    listeGalaxiesAuteur = []
    for X in range(0, nbreGalaxies):
        if presence_auteur_galaxie_liste_noeuds(nomAuteur, dirGalaxies[str(X)], path_file_galaxies):
            listeGalaxiesAuteur.append(X)
    dirGalaxies.close()
    return listeGalaxiesAuteur


def galaxies_liste_noms_auteur(liste_noms_auteurs, path_file_galaxies, path_file_list_galaxies):
    list_nom_auteurs_lower = [name.lower() for name in liste_noms_auteurs]
    dirGalaxies = shelve.open(path_file_list_galaxies)
    nbreGalaxies = dirGalaxies['nbreGalaxies']
    listeGalaxiesAuteur = []
    for X in range(0, nbreGalaxies):
        if presence_liste_nom_auteur_galaxie_liste_noeuds(list_nom_auteurs_lower, dirGalaxies[str(X)], path_file_galaxies):
            listeGalaxiesAuteur.append(X)
    dirGalaxies.close()
    return listeGalaxiesAuteur


def galaxies_listes_noms_auteurs(LNomsAuteurs, path_file_galaxies, path_file_list_galaxies):
    """ Attention, `LNomsAuteurs` est une liste de listes. """
    LNomsAuteursMin = []
    for nomsAuteur in LNomsAuteurs:
        LNomsAuteurMin = []
        for nomAuteur in nomsAuteur:
            LNomsAuteurMin.append(str.lower(nomAuteur))
        LNomsAuteursMin.append(LNomsAuteurMin)

    dirGalaxies = shelve.open(path_file_list_galaxies)
    nbreGalaxies = dirGalaxies['nbreGalaxies']
    listeGalaxiesAuteur = []
    for X in range(0, nbreGalaxies):
        LNoeuds = dirGalaxies[str(X)]
        if presence_auteurs_liste_noeuds(LNomsAuteursMin, LNoeuds, path_file_galaxies, path_file_list_galaxies):
            listeGalaxiesAuteur.append(X)
    dirGalaxies.close()
    return listeGalaxiesAuteur


def presence_auteurs_liste_noeuds(LNomsAuteurs, LNoeuds, path_file_galaxies, path_file_list_galaxies):
    for LNomsAuteurMin in LNomsAuteurs:
        if not presence_liste_nom_auteur_galaxie_liste_noeuds(LNomsAuteurMin, LNoeuds, path_file_galaxies):
            return ()
    return True


def ordonner(LGalaxies, path_file_galaxies):
    connexion = db.connexion(path_file_galaxies)
    curseur = connexion.cursor()
    L = sorted(LGalaxies, key=lambda galaxie: -degre_galaxie(galaxie, curseur))
    connexion.close()
    return L


def galaxies_auteur_ordonnees(Auteur, path_file_galaxies, path_file_list_galaxies):
    return ordonner(galaxies_auteur(Auteur, path_file_galaxies, path_file_list_galaxies), path_file_galaxies)


def galaxies_noms_auteur_ordonnees(LNomsAuteur, path_file_galaxies, path_file_list_galaxies):
    return ordonner(galaxies_liste_noms_auteur(LNomsAuteur, path_file_galaxies, path_file_list_galaxies),
                    path_file_galaxies)


def galaxies_noms_auteurs_ordonnees(LNomsAuteurs, path_file_galaxies, path_file_list_galaxies):
    return ordonner(galaxies_listes_noms_auteurs(LNomsAuteurs, path_file_galaxies, path_file_list_galaxies),
                    path_file_galaxies)


def presence_mot_titre_galaxie_liste_noeuds(Mot, listeNoeuds, path_file_galaxies):
    connexion = db.connexion(path_file_galaxies)
    curseur = connexion.cursor()
    reutilisations = set()
    for Noeud in listeNoeuds:
        curseur.execute(
            """ SELECT idReutilisation FROM grapheGalaxiesCible WHERE idNoeud = (?) """, (Noeud,))
        L = curseur.fetchall()
        if L != []:
            reutilisations.add(L[0][0])
        curseur.execute(
            """ SELECT idReutilisation FROM grapheGalaxiesSource WHERE idNoeud = (?) """, (Noeud,))
        L = curseur.fetchall()
        if L != []:
            reutilisations.add(L[0][0])
    for idReutilisation in reutilisations:
        curseur.execute(""" SELECT idRefSource FROM grapheReutilisations WHERE rowid = (?) """,
                        (str(idReutilisation),))
        t1 = curseur.fetchall()[0]
        curseur.execute(
            """ SELECT titre FROM livres WHERE rowid = (?) """, (t1[0],))
        if Mot in str.lower(curseur.fetchall()[0][0]):
            return Mot
        curseur.execute(""" SELECT idRefCible FROM grapheReutilisations WHERE rowid = (?) """,
                        (str(idReutilisation),))
        t1 = curseur.fetchall()[0]
        curseur.execute(
            """ SELECT titre FROM livres WHERE rowid = (?) """, (t1[0],))
        if Mot in str.lower(curseur.fetchall()[0][0]):
            return Mot
    connexion.close()
    return ()


def galaxies_titre_mot(Mot, path_file_galaxies, path_file_list_galaxies):
    nomMot = str.lower(Mot)
    dirGalaxies = shelve.open(path_file_list_galaxies)
    nbreGalaxies = dirGalaxies['nbreGalaxies']

    listeGalaxiesMot = []
    for X in range(0, nbreGalaxies):
        if presence_mot_titre_galaxie_liste_noeuds(nomMot, dirGalaxies[str(X)], path_file_galaxies):
            listeGalaxiesMot.append(X)
    dirGalaxies.close()
    return listeGalaxiesMot


def presence_auteur_galaxie(nom, galaxie, path_file_galaxies, path_file_list_galaxies):
    nom = nom.lower()
    for auteur in extraction_galaxies.auteurs_galaxie(galaxie, path_file_galaxies, path_file_list_galaxies):
        if nom in auteur.lower():
            return True
    return False
