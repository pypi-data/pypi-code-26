import os
import gi

gi.require_version('Gtk', '3.0')

from gi.repository import Gtk, Gdk
from galaxies.src.gui.gui_tools import intersection


class GtkTabFiltre:
	def __init__(self, gui):
		self.window = Gtk.Window(title="Tableau des filtres")
		self.gui = gui
		self.path = None
		self.grid = Gtk.Grid()
		self.box = Gtk.VBox()
		self.grid.set_column_homogeneous(True)
		self.grid.set_row_homogeneous(True)

		self.store = self.get_data()
		self.tableau =  Gtk.TreeView(self.store)
		
		self.manage_columns()
		self.add_scrollbar()


		self.button = Gtk.Button("Supprimer la selection")
		self.button.connect('clicked', self.supprimer)
		self.grid.add(self.tableau)
		
		self.box.pack_start(self.grid, True, True, 0)
		self.box.pack_start(self.button, False, False, 0)
		self.window.add(self.box)

		self.window.connect("delete-event", Gtk.main_quit)
		self.window.show_all()
		Gtk.main()


	def get_data(self):
		info = self.gui.list_filter_graph
		store = Gtk.ListStore(int, str, str, bool)
		for i in range(len(info)):
			if info[i] != None:
				store.append([i, info[i][0], str(info[i][1]), info[i][2]])
		return store


	def manage_columns(self):
		renderer = Gtk.CellRendererText()
		self.tableau_selection = self.tableau.get_selection()
		self.tableau_selection.connect("changed", self.get_id)
		columns = [Gtk.TreeViewColumn("Id", renderer, text=0), \
				   Gtk.TreeViewColumn("Type de filtre", renderer, text=1), \
				   Gtk.TreeViewColumn("Filtre", renderer, text=2), \
				   Gtk.TreeViewColumn("Inversé", renderer, text=3)]
		for column in columns:
			self.tableau.append_column(column)


	def add_scrollbar(self):
		self.scrollable_treelist = Gtk.ScrolledWindow()
		self.scrollable_treelist.set_vexpand(True)
		self.grid.attach(self.scrollable_treelist, 0, 0, 800, 50)
		self.scrollable_treelist.add(self.tableau)


	def get_id(self, selection):
		self.model, self.path = selection.get_selected_rows()


	def supprimer(self, button):
		if self.path != None:
			tree_iter = self.model.get_iter(self.path)
			i = self.model[tree_iter][0]
			print(i)
			if self.model[tree_iter][1] == "auteur" and self.model[tree_iter][3] == False:
				self.gui.already_filter_author = False
			elif self.model[tree_iter][1] == "date" and self.model[tree_iter][3] == False:
				self.gui.already_filter_date = False


			self.gui.noeud_filtre_ne_pas_supprimer[i] = [-1]
			self.gui.noeud_filtre_a_supprimer[i] = [-1]
			self.gui.list_filter_graph[i] = None
			self.model.remove(tree_iter)
			self.gui.graphe = Graph(self.gui.graphe_copie)
			self.gui.node_to_data()
			self.gui.taille_couleur_noeuds()

			l = []
			for i in self.gui.noeud_filtre_a_supprimer:
				for j in i:
					if j not in l and j != -1:
						l.append(j)
			if l != []:
				if len(l) == 1:
					l = l[0]
				self.gui.graphe.remove_vertex(l)

			self.gui.l.destroy()
			position = sfdp_layout(self.gui.graphe)
			self.gui.l = GraphWidget(self.gui.graphe, pos=position, display_props=self.gui.property_label_plus_texte, vertex_fill_color=self.gui.property_vertex_couleur, vertex_size=self.gui.property_vertex_taille)
			self.gui.l.set_size_request(self.gui.window.get_screen().get_width() -400, self.gui.window.get_screen().get_height () -400)
			self.gui.haut_droite.pack_start(self.gui.l, True, True, 0)
			self.gui.tableau.filtre()
			self.gui.window.show_all()




if __name__ == '__main__':
	GtkTab("results/galaxies.db")
