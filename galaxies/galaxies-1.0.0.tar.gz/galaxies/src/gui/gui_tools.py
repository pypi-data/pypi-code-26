import sqlite3 
import numpy as np

def get_father_son(path):
	connection = sqlite3.connect(path)
	cursor = connection.cursor()
	cursor.execute("SELECT * FROM grapheGalaxies")
	rows = cursor.fetchall()
	connection.close()
	return rows
	
def get_authors_date(path):
	connection = sqlite3.connect(path)
	cursor = connection.cursor()
	cursor.execute("SELECT DISTINCT auteur FROM livres")
	authors = cursor.fetchall()
	cursor.execute("SELECT DISTINCT date FROM livres")
	date = cursor.fetchall()
	connection.close()
	return authors, date
	
def get_node_info(path, father, son):
	connection = sqlite3.connect(path)
	cursor = connection.cursor()
	cursor.execute("SELECT DISTINCT l1.titre, l1.auteur, l1.date, l2.titre, l2.auteur, l2.date \
					FROM grapheReutilisations r, grapheGalaxiesSource s, grapheGalaxiesCible c, livres l1, livres l2\
					WHERE s.idReutilisation = r.rowid and c.idReutilisation = r.rowid and r.idRefSource = l1.rowid and \
						  r.idRefCible = l2.rowid and s.idNoeud = " + str(father) + " and c.idNoeud = " + str(son))
	res = cursor.fetchall()
	connection.close()
	return res[0]

def get_filtre(path, choix, inverse, filtre ):
	###Seulement pere filtré pour le moment
	inv = ""
	connection = sqlite3.connect(path)
	cursor = connection.cursor()

	if inverse:
		inv = "!"

	if choix == "année":
		cursor.execute("SELECT DISTINCT gg.idNoeudPere, gg.idNoeudFils FROM grapheReutilisations gr, grapheGalaxiesSource s, grapheGalaxiesCible c, grapheGalaxies gg, livres l\
								WHERE l.rowid = gr.idRefSource and gr.rowid = s.idReutilisation and  s.idNoeud = gg.idNoeudPere and l.date"+ inv + "= " + str(filtre))
	elif choix == "auteur":
		filtre = "'" + filtre + "'"
		cursor.execute("SELECT DISTINCT gg.idNoeudPere, gg.idNoeudFils FROM grapheReutilisations gr, grapheGalaxiesSource s, grapheGalaxiesCible c, grapheGalaxies gg, livres l\
								WHERE l.rowid = gr.idRefSource and gr.rowid = s.idReutilisation and  s.idNoeud = gg.idNoeudPere and l.auteur" + inv + "= " + filtre)
	rows = cursor.fetchall()
	connection.close()
	
	return rows

def get_text(path, father, son):
	connection = sqlite3.connect(path)
	cursor = connection.cursor()
	cursor.execute("SELECT DISTINCT r.texteSource, r.texteCible FROM grapheReutilisations r, grapheGalaxiesSource s, grapheGalaxiesCible c WHERE s.idReutilisation = c.idReutilisation and s.idReutilisation = r.rowid and s.idNoeud = " + str(father) + " and c.idNoeud = " + str(son))
	text = cursor.fetchall()
	if text == []:
		cursor.execute("SELECT DISTINCT r.texteSource, r.texteCible FROM grapheReutilisations r, grapheGalaxiesSource s, grapheGalaxiesCible c WHERE s.idReutilisation = c.idReutilisation and s.idReutilisation = r.rowid and s.idNoeud = " + str(son) + " and c.idNoeud = " + str(father))
		text = cursor.fetchall()
	connection.close()
	return text[0]


def get_all_galaxies_info(path):
	connection = sqlite3.connect(path)
	cursor = connection.cursor()
	cursor.execute("SELECT DISTINCT * FROM degreGalaxies")
	info = cursor.fetchall()
	connection.close()
	return info


def get_size_node(path, father, son):
	t = get_text(path, father, son)
	return (len(t[0]), len(t[1]))


def intersection(L):
	new_list = L[0]
	for i in range(1, len(L)):
		t = []
		for e in new_list:
			if e in L[i]:
				t.append(e) 
		new_list = t
	return new_list

def get_equivalent(dico_id_label):
	dico_label_id = {}
	for i in dico_id_label:
		if dico_id_label[i] in dico_label_id:
			dico_label_id[dico_id_label[i]].append(i)
		else:
			dico_label_id[dico_id_label[i]] = [i]
	return dico_label_id

def get_equivalent_id(id_node, dico_label_id):
	for label in dico_label_id:
		if id_node in dico_label_id[label]:
			copy = list(dico_label_id[label])
			copy.remove(id_node)
			return copy[0]

if __name__ == '__main__':
	a = get_equivalent({0: '153115', 1: '11', 2: '11', 3: '153115'})
	print(get_equivalent_id(2, a))



