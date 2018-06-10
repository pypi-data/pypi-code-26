# -*- coding: utf-8 -*-

import time
import shelve
import os

from progressbar import ProgressBar, Percentage, Counter, Timer

import galaxies.src.core.database_tools as db


PB_WIDGETS = ["Processed: ", Counter(), " nodes [", Percentage(), "], ",
              Timer()]

MESSAGE_NODES_PROCESSED = "{} nodes processed."


class Galaxie:
    """ Permet d'énumérer les composantes connexes. """
    def __init__(self, path_file_galaxies, path_file_list_galaxies):
        self.val = 0
        self.compositionGalaxie = dict()
        self.path_file_galaxies = path_file_galaxies
        self.path_file_list_galaxies = path_file_list_galaxies

    def nouvelle_valeur(self):
        self.val += 1

    def noeuds_galaxie(self, n, L):
        self.compositionGalaxie[n] = L
        return len(L)

    def save(self):
        list_galaxies = shelve.open(self.path_file_list_galaxies)
        x = 0
        while x < self.val:
            list_galaxies[str(x)] = self.compositionGalaxie[x]
            x += 1
        list_galaxies['nbreGalaxies'] = self.val
        list_galaxies.close()

    def rangement(self):
        tr = time.clock()
        print("Galaxies successfuly extracted, now cleaning.")
        connexion = db.connexion(self.path_file_galaxies)
        curseur = connexion.cursor()
        curseur.execute("""INSERT INTO nombreGalaxies values (?) """, (str(self.val),))
        print("Nombre de galaxies: "+str(self.val))
        i = 0
        while i < self.val:
            lnoeuds = self.compositionGalaxie[i]
            n = len(lnoeuds)
            longueur = 0
            for texte in texte_galaxie(i, curseur, self.path_file_list_galaxies):
                longueur += len(texte)
            curseur.execute("""DELETE from degreGalaxies WHERE idGalaxie = ?""", (str(i),))
            curseur.execute("""INSERT INTO degreGalaxies values (?,?, ?, ?) """, (str(i),str(n),str(longueur),str(int(longueur/n)),))
            i += 1
        connexion.commit()
        connexion.close()
        trf = time.clock()
        print("Galaxies successfuly cleaned. Time : " + format(trf - tr, 'f') + " second(s)")


class NoeudMarques:
    def __init__(self, max_noeuds):
        self.max_noeuds = max_noeuds
        self.noeuds = {n: "non" for n in range(max_noeuds)}

    def noeud_non_visite(self, noeudCourant):
        for n in range(noeudCourant, self.max_noeuds):
            if self.noeuds[n] == 'non':
                return n

    def affectation_galaxie(self, n, g):
        if self.noeuds[n] != 'non':
            print("Erreur sur affectation galaxie au noeud " + str(n) + " - précédente affectation: " + str(self.noeuds[str(n)]))
            return 'erreur'
        else:
            self.noeuds[n] = g.val

    def galaxie(self, n):
        g = self.noeuds[n]
        if g == 'non':
            return 'erreur'
        else:
            return g


def extraction_composantes_connexes(path_file_galaxies: str,
                                    path_file_list_galaxies: str,
                                    path_file_adjacency_graph: str,
                                    path_file_adjacency_graph_transposed: str,
                                    max_noeud: int,):
    graphe = shelve.open(path_file_adjacency_graph)
    graphe_t = shelve.open(path_file_adjacency_graph_transposed)

    noeuds = NoeudMarques(max_noeud)
    galaxie = Galaxie(path_file_galaxies, path_file_list_galaxies)
    nouveauNoeud = noeuds.noeud_non_visite(0)
    while nouveauNoeud != None:  # < maxNoeud:
        galaxie.noeuds_galaxie(galaxie.val, composante_connexe(nouveauNoeud, galaxie, graphe, graphe_t, noeuds))
        galaxie.nouvelle_valeur()
        nouveauNoeud = noeuds.noeud_non_visite(nouveauNoeud)
    graphe_t.close()
    graphe.close()
    galaxie.save()
    galaxie.rangement()
    return galaxie


def extraction_composantes_connexes_(path_file_galaxies: str,
                                     path_file_list_galaxies: str,
                                     max_noeud: int,):
    # Connexion to the database
    connexion = db.connexion(path_file_galaxies)
    curseur = connexion.cursor()

    # Initialise the progress-bar
    progress_bar = ProgressBar(widgets=PB_WIDGETS, maxval=max_noeud)
    progress_bar.start()

    # Initialise of the Node and Galaxy structures
    noeuds = NoeudMarques(max_noeud)
    galaxie = Galaxie(path_file_galaxies, path_file_list_galaxies)

    nouveau_noeud = noeuds.noeud_non_visite(0)
    while nouveau_noeud is not None:  # < max_noeud:
        galaxie.noeuds_galaxie(galaxie.val, composante_connexe_(nouveau_noeud, galaxie, curseur, noeuds))
        galaxie.nouvelle_valeur()
        progress_bar.update(nouveau_noeud + 1)
        nouveau_noeud = noeuds.noeud_non_visite(nouveau_noeud)
    progress_bar.finish()
    galaxie.save()
    galaxie.rangement()
    connexion.close()
    return galaxie


def composante_connexe(N, g, graphe, graphe_t, noeuds):
    ensemble_noeuds = set()
    ensemble_noeuds.add(N)

    noeuds_visites = set()
    while len(ensemble_noeuds) != 0:
        ensemble_noeuds = ensemble_noeuds.difference(noeuds_visites)
        ensemble = ensemble_noeuds.pop()
        if ensemble not in noeuds_visites:
            noeuds.affectation_galaxie(ensemble, g)
            ensemble_noeuds.update(fils(ensemble, graphe, graphe_t))
            noeuds_visites.add(ensemble)

        ensemble_noeuds = ensemble_noeuds.difference(noeuds_visites)
        if ensemble_noeuds.intersection(noeuds_visites) != set():
            print("attention!! Noeud " + str(ensemble))
    return noeuds_visites


def fils(X, graphe, graphe_t):
    return graphe[str(X)] + graphe_t[str(X)]


def composante_connexe_(nouveau_noeud, galaxie, curseur, noeuds):
    ensemble_noeuds = set()
    ensemble_noeuds.add(nouveau_noeud)

    noeudsVisites = set()
    while len(ensemble_noeuds) != 0:
        ensemble = ensemble_noeuds.pop()
        if ensemble not in noeudsVisites:
            noeuds.affectation_galaxie(ensemble, galaxie)
            ensemble_noeuds.update(fils_(ensemble, curseur))
            noeudsVisites.add(ensemble)
    return noeudsVisites


def fils_(X, curseur):
    curseur.execute(""" SELECT idNoeudFils FROM grapheGalaxies WHERE idNoeudPere = (?) """, (X,))
    return [res[0] for res in curseur.fetchall()]


def cible(arc, curseur):
    curseur.execute(""" SELECT idNoeud FROM grapheGalaxiesCible WHERE idReutilisation = (?) """, (arc,))
    return curseur.fetchall()


def source(arc, curseur):
    curseur.execute(""" SELECT idNoeud FROM grapheGalaxiesSource WHERE idReutilisation = (?) """, (arc,))
    return curseur.fetchall()


def textes_galaxie(numero, path_file_galaxies, path_file_list_galaxies):
    dirGalaxies = shelve.open(path_file_list_galaxies)
    ListeNoeuds = dirGalaxies[str(numero)]
    dirGalaxies.close()

    connexion = db.connexion(path_file_galaxies)
    curseur = connexion.cursor()

    reutilisations = set()
    for Noeud in ListeNoeuds:
        curseur.execute(""" SELECT idReutilisation FROM grapheGalaxiesCible WHERE idNoeud = (?) """, (Noeud,))
        L = curseur.fetchall()
        if L != []:
            reutilisations.add(L[0][0])
        curseur.execute(""" SELECT idReutilisation FROM grapheGalaxiesSource WHERE idNoeud = (?) """, (Noeud,))
        L = curseur.fetchall()
        if L != []:
            reutilisations.add(L[0][0])
    textes = set()
    for idReutilisation in reutilisations:
        curseur.execute(""" SELECT texteSource, idRefSource FROM grapheReutilisations WHERE rowid = (?) """, (str(idReutilisation),))
        textes.add(curseur.fetchall()[0][0])
        curseur.execute(""" SELECT texteCible, idRefCible FROM grapheReutilisations WHERE rowid = (?) """, (str(idReutilisation),))
        textes.add(curseur.fetchall()[0][0])
    connexion.close()
    return textes


def texte_galaxie(numero, curseur, path_file_list_galaxies):
    dirGalaxies = shelve.open(path_file_list_galaxies)
    ListeNoeuds = dirGalaxies[str(numero)]
    dirGalaxies.close()

    reutilisations = set()
    for Noeud in ListeNoeuds:
        curseur.execute(""" SELECT idReutilisation FROM grapheGalaxiesCible WHERE idNoeud = (?) """, (Noeud,))
        L = curseur.fetchall()
        if L != []:
            reutilisations.add(L[0][0])
        curseur.execute(""" SELECT idReutilisation FROM grapheGalaxiesSource WHERE idNoeud = (?) """, (Noeud,))
        L = curseur.fetchall()
        if L != []:
            reutilisations.add(L[0][0])

    textes = set()
    for idReutilisation in reutilisations:
        curseur.execute(""" SELECT texteSource, idRefSource FROM grapheReutilisations WHERE rowid = (?) """, (str(idReutilisation),))
        textes.add(curseur.fetchall()[0][0])
        curseur.execute(""" SELECT texteCible, idRefCible FROM grapheReutilisations WHERE rowid = (?) """, (str(idReutilisation),))
        textes.add(curseur.fetchall()[0][0])
    return textes


def auteurs_galaxie(numero, path_file_galaxies, path_file_list_galaxies):
    dirGalaxies = shelve.open(path_file_list_galaxies)
    ListeNoeuds = dirGalaxies[str(numero)]
    dirGalaxies.close()

    connexion = db.connexion(path_file_galaxies)
    curseur = connexion.cursor()

    reutilisations = set()
    for Noeud in ListeNoeuds:
        curseur.execute(""" SELECT idReutilisation FROM grapheGalaxiesCible WHERE idNoeud = (?) """, (Noeud,))
        L = curseur.fetchall()
        if L != []:
            reutilisations.add(L[0][0])
        curseur.execute(""" SELECT idReutilisation FROM grapheGalaxiesSource WHERE idNoeud = (?) """, (Noeud,))
        L = curseur.fetchall()
        if L != []:
            reutilisations.add(L[0][0])

    auteurs = set()
    for idReutilisation in reutilisations:
        curseur.execute(""" SELECT idRefSource FROM grapheReutilisations WHERE rowid = (?) """,
                        (str(idReutilisation),))
        t1 = curseur.fetchall()[0]
        curseur.execute(""" SELECT auteur FROM livres WHERE rowid = (?) """, (t1[0],))
        auteurs.add(curseur.fetchall()[0][0])
        curseur.execute(""" SELECT idRefCible FROM grapheReutilisations WHERE rowid = (?) """,
                        (str(idReutilisation),))
        t1 = curseur.fetchall()[0]
        curseur.execute(""" SELECT auteur FROM livres WHERE rowid = (?) """, (t1[0],))
        auteurs.add(curseur.fetchall()[0][0])
    connexion.close()
    return auteurs


def textes_et_references_galaxie(numero, path_file_galaxies, path_file_list_galaxies):
    dirGalaxies = shelve.open(path_file_list_galaxies)
    ListeNoeuds = dirGalaxies[str(numero)]
    dirGalaxies.close()
    connexion = db.connexion(path_file_galaxies)
    curseur = connexion.cursor()
    reutilisations = set()
    for Noeud in ListeNoeuds:
        curseur.execute(""" SELECT idReutilisation FROM grapheGalaxiesCible WHERE idNoeud = (?) """, (Noeud,))
        L = curseur.fetchall()
        if L != []:
            reutilisations.add(L[0][0])
        curseur.execute(""" SELECT idReutilisation FROM grapheGalaxiesSource WHERE idNoeud = (?) """, (Noeud,))
        L = curseur.fetchall()
        if L != []:
            reutilisations.add(L[0][0])
    textes = set()
    for idReutilisation in reutilisations:
        curseur.execute(""" SELECT texteSource, idRefSource FROM grapheReutilisations WHERE rowid = (?) """, (str(idReutilisation),))
        t1 = curseur.fetchall()[0]
        curseur.execute(""" SELECT auteur, titre, date FROM livres WHERE rowid = (?) """, (t1[1],))
        textes.add((t1[0], curseur.fetchall()[0]))
        curseur.execute(""" SELECT texteCible, idRefCible FROM grapheReutilisations WHERE rowid = (?) """, (str(idReutilisation),))
        t1 = curseur.fetchall()[0]
        curseur.execute(""" SELECT auteur, titre, date FROM livres WHERE rowid = (?) """, (t1[1],))
        textes.add((t1[0], curseur.fetchall()[0]))
    connexion.close()
    return textes


def textes_liste_noeuds(ListeNoeuds, path_file_galaxies):
    connexion = db.connexion(path_file_galaxies)
    curseur = connexion.cursor()
    reutilisations = set()
    for Noeud in ListeNoeuds:
        curseur.execute(""" SELECT idReutilisation FROM grapheGalaxiesCible WHERE idNoeud = (?) """, (Noeud,))
        L = curseur.fetchall()
        if L != []:
            reutilisations.add(L[0][0])
        curseur.execute(""" SELECT idReutilisation FROM grapheGalaxiesSource WHERE idNoeud = (?) """, (Noeud,))
        L = curseur.fetchall()
        if L != []:
            reutilisations.add(L[0][0])
    textes = set()
    for idReutilisation in reutilisations:
        curseur.execute(""" SELECT texteSource, idRefSource FROM grapheReutilisations WHERE rowid = (?) """, (str(idReutilisation),))
        textes.add(curseur.fetchall()[0][0])
        curseur.execute(""" SELECT texteCible, idRefCible FROM grapheReutilisations WHERE rowid = (?) """, (str(idReutilisation),))
        textes.add(curseur.fetchall()[0][0])
    connexion.close()
    return textes


def textes_et_references_liste_noeuds(ListeNoeuds, path_file_galaxies):
    connexion = db.connexion(path_file_galaxies)
    curseur = connexion.cursor()
    reutilisations = set()
    for Noeud in ListeNoeuds:
        curseur.execute(""" SELECT idReutilisation FROM grapheGalaxiesCible WHERE idNoeud = (?) """, (Noeud,))
        L = curseur.fetchall()
        if L != []:
            reutilisations.add(L[0][0])
        curseur.execute(""" SELECT idReutilisation FROM grapheGalaxiesSource WHERE idNoeud = (?) """, (Noeud,))
        L = curseur.fetchall()
        if L != []:
            reutilisations.add(L[0][0])
    textes = set()
    for idReutilisation in reutilisations:
        curseur.execute(""" SELECT texteSource, idRefSource FROM grapheReutilisations WHERE rowid = (?) """,
                        (str(idReutilisation),))
        t1 = curseur.fetchall()[0]
        curseur.execute(""" SELECT auteur, titre, date FROM livres WHERE rowid = (?) """, (t1[1],))
        textes.add((t1[0],curseur.fetchall()[0]))
        curseur.execute(""" SELECT texteCible, idRefCible FROM grapheReutilisations WHERE rowid = (?) """,
                        (str(idReutilisation),))
        t1 = curseur.fetchall()[0]
        curseur.execute(""" SELECT auteur, titre, date FROM livres WHERE rowid = (?) """, (t1[1],))
        textes.add((t1[0], curseur.fetchall()[0]))
    connexion.close()
    return textes


def textes_et_references_liste_noeuds_avec_noeuds(ListeNoeuds, path_file_galaxies):
    connexion = db.connexion(path_file_galaxies)
    curseur = connexion.cursor()
    reutilisations = set()
    for Noeud in ListeNoeuds:
        curseur.execute(""" SELECT idReutilisation FROM grapheGalaxiesCible WHERE idNoeud = (?) """, (Noeud,))
        L = curseur.fetchall()
        if L != []:
            reutilisations.add((L[0][0],Noeud))
        curseur.execute(""" SELECT idReutilisation FROM grapheGalaxiesSource WHERE idNoeud = (?) """, (Noeud,))
        L = curseur.fetchall()
        if L != []:
            reutilisations.add((L[0][0], Noeud))
    textes = set()
    for idReutilisation in reutilisations:
        curseur.execute(""" SELECT texteSource, idRefSource FROM grapheReutilisations WHERE rowid = (?) """, (str(idReutilisation[0]),))
        t1 = curseur.fetchall()[0]
        curseur.execute(""" SELECT auteur, titre, date FROM livres WHERE rowid = (?) """, (t1[1],))
        textes.add((t1[0],curseur.fetchall()[0], idReutilisation[1]))
        curseur.execute(""" SELECT texteCible, idRefCible FROM grapheReutilisations WHERE rowid = (?) """, (str(idReutilisation[0]),))
        t1 = curseur.fetchall()[0]
        curseur.execute(""" SELECT auteur, titre, date FROM livres WHERE rowid = (?) """, (t1[1],))
        textes.add((t1[0], curseur.fetchall()[0],idReutilisation[1]))
    connexion.close()
    return textes


def composantes_extraites(path_file_list_galaxies: str) -> bool:
    """ Vérifie si les composantes ont déjà été extraites. """
    if os.path.isfile(path_file_list_galaxies) is not None:
        try:
            _ = shelve.open(path_file_list_galaxies)['nbreGalaxies']
            return True
        except KeyError:
            pass
    return False


if __name__ == "__main__":
    pass
