import os
import gi

gi.require_version('Gtk', '3.0')

from gi.repository import Gtk, Gdk
from galaxies.src.gui.gui_tools import get_equivalent_id

class GtkTabBas:
	def __init__(self, gui, tab):
		self.gui = gui
		child = self.gui.sw2.get_children()
		if child != []:
			self.gui.sw2.remove(child[0])
		self.grid = Gtk.Grid()
		self.grid.set_column_homogeneous(True)
		self.grid.set_row_homogeneous(True)

		self.store = self.get_data(tab)
		self.tableau =  Gtk.TreeView(self.store)
		
		self.manage_columns()
		self.add_scrollbar()

		self.gui.sw2.add(self.grid)
		self.gui.sw2.set_margin_top(3)
		self.gui.window.show_all()


	def get_data(self, tab):
		tab = self.get_tuple_donnees(tab)
		store = Gtk.ListStore(str, str, str, int, str)
		for donnees in tab:
			store.append([donnees[0], donnees[1], donnees[2], donnees[3], donnees[4]])
		return store


	def get_tuple_donnees(self, tab):
		new_tab = []
		memoire = []
		for id_noeud in tab[0]:
			t = []
			label = tab[0][id_noeud]
			if label not in memoire:
				t.append(label)
				t.append(tab[1][id_noeud])
				t.append(tab[2][id_noeud])
				t.append(tab[3][id_noeud])
				t.append(tab[4][id_noeud])
				new_tab.append(t)
				memoire.append(label)
		return new_tab


	def manage_columns(self):
		renderer = Gtk.CellRendererText()
		self.tableau_selection = self.tableau.get_selection()
		columns = [Gtk.TreeViewColumn("Label", renderer, text=0), \
				   Gtk.TreeViewColumn("Titre", renderer, text=1), \
				   Gtk.TreeViewColumn("Auteur", renderer, text=2), \
				   Gtk.TreeViewColumn("Date", renderer, text=3),\
				   Gtk.TreeViewColumn("Réutilisation", renderer, text=4)]
		for column in columns:
			self.tableau.append_column(column)


	def add_scrollbar(self):
		self.scrollable_treelist = Gtk.ScrolledWindow()
		self.scrollable_treelist.set_vexpand(True)
		self.grid.attach(self.scrollable_treelist, 0, 0, 800, 500)
		self.scrollable_treelist.add(self.tableau)



	def get_id(self, selection):
		if self.open:
			self.open = False
			return
		model, path = selection.get_selected_rows()
		if path != None:
			self.gui.display_galaxie(model[path][0])


	def filtre(self):
		for row in self.store:
			self.store.remove(row.iter)

		for v in self.gui.graphe.vertices():
			label = self.gui.property_vertex_label[v]
			titre = self.gui.property_vertex_titre[v]
			auteur = self.gui.property_vertex_auteur[v]
			date = self.gui.property_vertex_date[v]
			texte = self.gui.property_vertex_texte[v] 
			self.store.append([label, titre, auteur, date, texte])



if __name__ == '__main__':
	GtkTab("results/galaxies.db")

