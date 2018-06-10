# -*- coding: utf-8 -*-

import sqlite3
import shelve
import subprocess
import codecs
import re

import galaxies.src.core.extraction_galaxies as extraction_galaxies
import galaxies.src.core.extraction_galaxies_new as extraction_galaxies_new
from galaxies.src.common.maths import is_int
import galaxies.src.core.database_tools as db

__author__ = 'Jean-Gabriel Ganascia'


class ConstructionAmas:
    def __init__(self, galaxy, path_file_galaxies, path_file_list_galaxies, path_file_degre_noeuds_galaxy,
                 path_file_galaxy_graphe):
        filling_galaxy_graph(galaxy, path_file_galaxies, path_file_list_galaxies, path_file_degre_noeuds_galaxy,
                             path_file_galaxy_graphe)
        self.galaxie = galaxy
        graphText = parametres.DirAmas + "/galaxie_graphe.txt"
        graphBin = parametres.DirAmas + '/galaxie_graphe.bin'
        self.graphTree = parametres.DirAmas + '/galaxie_graphe.tree'
        self.transduction = parametres.DirAmas + '/labelings_connection_file.txt'
        subprocess.run([parametres.DirLouvain + '/./convert', '-i', graphText, '-o', graphBin, '-r', self.transduction])
        command2 = "'" + parametres.DirLouvain + "/./louvain' " + graphBin + ' -l -1 -q id_qual > ' + self.graphTree
        L = subprocess.run(command2, shell=True)
        self.constructionDictionnaire()
        self.nombreGroupes = len(self.groupe.keys())
        print("Nombre de groupes: " + str(self.nombreGroupes))

    def constructionDictionnaire(self):
        self.dictTransduction = dict()
        FichierEntree = codecs.open(self.transduction, 'r')
        E = FichierEntree.readline()
        # nbr_lignes = 0
        while E != "":
            # nbr_lignes += 1
            L = re.split(' ', E)
            # print("L: "+str(L)+"1: "+str(L[1][:-1])+" - 2: "+str(L[0]))
            self.dictTransduction[L[1][:-1]] = L[0]
            E = FichierEntree.readline()
        # self.nbre_noeuds = nbr_lignes
        FichierEntree.close()
        # self.arbre = dict()
        self.groupe = dict()
        self.FichierGraphe = codecs.open(self.graphTree, 'r')
        E = self.FichierGraphe.readline()
        while E != "":
            L = re.split(' ', E)
            if L[1][:-1] in self.groupe.keys():
                self.groupe[L[1][:-1]].append(self.dictTransduction[L[0]])
            else:
                self.groupe[L[1][:-1]] = [self.dictTransduction[L[0]]]
            E = self.FichierGraphe.readline()
        self.FichierGraphe.close()

    def impression_tous_groupes_anciennete(self, p):
        i = 0
        while i < self.nombreGroupes:
            print("Groupe " + str(i + 1))
            L = sorted(extraction_galaxies.textes_et_references_liste_noeuds(self.groupe[str(i)]),
                       key=lambda reference: reference[1][2] + 1 / len(reference[0]))
            q = p
            while L != [] and (q > 0 or p == 0):
                E = L[0]
                L = L[1:]
                print("\t- " + str(E[0]) + "\nRéférences: " + str(E[1]) + "\n")
                q -= 1
            i += 1

    def generationFichiersGraphes_tous_groupes(self):
        i = 0
        while i < self.nombreGroupes:
            print("Génération graphe groupe " + str(i + 1))
            extraction_galaxies.sauve_graphe_amas(self.groupe[str(i)], str(self.galaxie), str(i + 1))
            i += 1

    def impression_groupe_anciennete(self, i, p):
        print("Impression groupe " + str(i))
        L = sorted(extraction_galaxies.textes_et_references_liste_noeuds(self.groupe[str(i - 1)]),
                   key=lambda reference: reference[1][2] + 1 / len(reference[0]))
        q = p
        while L != [] and (q > 0 or p == 0):
            E = L[0]
            L = L[1:]
            print("\t- " + str(E[0]) + "\nRéférences: " + str(E[1]) + "\n")
            q -= 1

    def impression_groupe_degre(self, i, p):
        degreNoeudsGalaxie = shelve.open(parametres.DirBD + '/degreNoeudsGalaxie')
        print("Impression groupe " + str(i))
        # L = extraction_galaxies.textesEtReferencesListeNoeuds_avecNoeuds(self.groupe[str(i-1)])
        # print(L)
        L = sorted(extraction_galaxies.textes_et_references_liste_noeuds_avec_noeuds(self.groupe[str(i - 1)]),
                   key=lambda reference: 1 / degreNoeudsGalaxie[reference[2]])
        q = p
        while L != [] and (q > 0 or p == 0):
            E = L[0]
            L = L[1:]
            print("\t- " + str(E[0]) + "\nRéférences: " + str(E[1]) + " degré: " + str(degreNoeudsGalaxie[E[2]]) + "\n")
            q -= 1
        degreNoeudsGalaxie.close()

    def impression_groupes(self):
        E = input("Galaxie n°" + str(self.galaxie) + " Quel groupe voulez-vous examiner? ")
        if E == 'q' or E == 'Q' or E == 'quitter':
            return
        elif not int(E):
            self.impression_groupes_degre()
        elif int(E) > 0 and int(E) <= self.nombreGroupes:
            self.impression_groupe_anciennete(int(E), 0)
            self.impression_groupes()
            return
        else:
            self.impression_groupes()

    def impression_groupes_degre(self):
        E = input("Galaxie n°" + str(self.galaxie) + " Quel groupe voulez-vous examiner? ")
        if E == 'q' or E == 'Q' or E == 'quitter' or E == "quit" or E == 'QUITTER' or E == "QUIT":
            return
        elif E == "" or not is_int(E):
            self.impression_groupes_degre()
        elif int(E) > 0 and int(E) <= self.nombreGroupes:
            self.impression_groupe_degre(int(E), 0)
            C = input(
                "\tGalaxie n°" + str(self.galaxie) + " - groupe " + str(E) + " - sauvegarde du graphe (Oui/Non): ")
            if C in ["Oui", "O", "oui", "o", "OUI", "Yes", "Y", "yes", "y"]:
                extraction_galaxies_new.sauve_graphe_amas(self.groupe[str(E)], str(self.galaxie), str(int(E) + 1))
            self.impression_groupes_degre()
            return
        else:
            print('Le nombre donné ne correspond pas à un numéro de groupe!')
            self.impression_groupes_degre()


# TODO: Trouver comment est créé 'path_file_degre_noeuds_galaxy' (anciennement : parametres.DirBD + '/degreNoeudsGalaxie')
# TODO: Trouver comment est créé 'path_file_galaxy_graphe' (anciennement : open(parametres.DirAmas+"/galaxie_graphe.txt", mode='wt'))
def filling_galaxy_graph(num_galaxy, path_file_galaxies, path_file_list_galaxies, path_file_degre_noeuds_galaxy,
                         path_file_galaxy_graphe):
    """ Open the file containing the `num_galaxy` galaxy, then build the amas from it. """
    with shelve.open(path_file_list_galaxies) as dirGalaxies:
        liste_noeuds = dirGalaxies[str(num_galaxy)]

    with shelve.open(path_file_degre_noeuds_galaxy) as degreNoeudsGalaxie, \
            db.connexion(path_file_galaxies) as connexion, \
            open(path_file_galaxy_graphe, mode='wt') as galaxy_graphe:
        cursor = connexion.cursor()
        for node in liste_noeuds:
            liste_fils = extraction_galaxies.fils_(node, cursor)
            degreNoeudsGalaxie[str(node)] = len(liste_fils)
            for fils in liste_fils:
                galaxy_graphe.write(str(node) + " " + str(fils) + "\n")


if __name__ == "__main__":
    pass
