import os
import gi

gi.require_version('Gtk', '3.0')

from gi.repository import Gtk, Gdk
from galaxies.src.gui.gui_tools import get_all_galaxies_info


class GtkTabInside:
	def __init__(self, gui, path):
		self.gui = gui
		self.grid = Gtk.Grid()
		self.grid.set_column_homogeneous(True)
		self.grid.set_row_homogeneous(True)
		self.store = self.get_data(path)
		self.tableau =  Gtk.TreeView(self.store)
		
		self.manage_columns()
		self.add_scrollbar()

		self.label = Gtk.Label("\nTableau des réutilisations\n")
		self.gui.sw.pack_start(self.label, False, False, 0)
		self.gui.sw.add(self.grid)
		self.gui.sw.set_margin_right(5)
		self.gui.window.show_all()


	def get_data(self, path):
		info = get_all_galaxies_info(path)
		store = Gtk.ListStore(int, int, int, int)
		for galaxie in info:
			print(galaxie)
			store.append([galaxie[0], galaxie[1], galaxie[2], galaxie[3]])
		return store


	def manage_columns(self):
		i = 0
		renderer = Gtk.CellRendererText()
		self.tableau_selection = self.tableau.get_selection()
		self.tableau_selection.connect("changed", self.get_id)
		columns = [Gtk.TreeViewColumn("Id", renderer, text=0), \
				   Gtk.TreeViewColumn("Nombre", renderer, text=1), \
				   Gtk.TreeViewColumn("Taille totale", renderer, text=2), \
				   Gtk.TreeViewColumn("Taille moyenne", renderer, text=3)]
		for column in columns:
			column.set_clickable(True) 
			column.set_sort_column_id(i)
			column.connect("clicked", lambda x="clicked", y=column: self.column_press(x, y))
			self.tableau.append_column(column)
			i += 1


	def add_scrollbar(self):
		self.scrollable_treelist = Gtk.ScrolledWindow()
		self.scrollable_treelist.set_vexpand(True)
		self.grid.attach(self.scrollable_treelist, 0, 0, 800, 500)
		self.scrollable_treelist.add(self.tableau)


	def column_press(self, event, column):
		self.store.set_sort_func(0, self.compare, None)


	def get_id(self, selection):
		model, path = selection.get_selected_rows()
		if path != None:
			self.gui.display_galaxie(model[path][0])


	def compare(self, model, row1, row2, user_data):
		""" http://python-gtk-3-tutorial.readthedocs.io/en/latest/treeview.html?highlight=treeview """
		sort_column, _ = model.get_sort_column_id()
		value1 = model.get_value(row1, sort_column)
		value2 = model.get_value(row2, sort_column)
		if value1 < value2:
			return -1
		elif value1 == value2:
			return 0
		else:
			return 1

	def filtre(self, list_id):
		copy = list(list_id)
		for row in self.store:
			if row[0] in copy:
				copy.pop(copy.index(row[0]))
				self.store.remove(row.iter)
		self.gui.window.show_all()




if __name__ == '__main__':
	GtkTab("results/galaxies.db")
