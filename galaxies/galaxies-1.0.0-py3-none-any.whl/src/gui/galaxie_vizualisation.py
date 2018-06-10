import os
import gi
import networkx as nx
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
from operator import itemgetter
from graph_tool.all import *
from galaxies.src.gui.gui_tools import *
from tkinter import *
from galaxies.src.gui.gtk_tab_inside import GtkTabInside
from galaxies.src.gui.gtk_tab_bas import GtkTabBas
from galaxies.src.gui.gtk_tab_filtres import GtkTabFiltre

#Tester d'ouvrir 1 graphe, faire des filtres et ouvrir un autre graph différent
class WindowsGalaxieVizualisation:
	def __init__(self):
		self.list_filter_graph = []
		# self.list_bool_already = [None]
		self.noeud_filtre_ne_pas_supprimer = []
		self.noeud_filtre_a_supprimer = []
		self.already_filter_date = False
		self.already_filter_author = False
		self.path = None
		self.galaxie_id = None
		self.first_creation = True
		self.window = Gtk.Window(title="Test")
		self.window.maximize()
	
			
		self.menubar = Gtk.MenuBar()
		
		self.menu1 = Gtk.Menu()
		self.menu1_file = Gtk.MenuItem("Fichier")
		self.menu1_file.set_submenu(self.menu1)
		
		self.menu2 = Gtk.Menu()
		self.menu2_filtre = Gtk.MenuItem("Filtre")
		self.menu2_filtre.set_submenu(self.menu2)
		
		self.menu3 = Gtk.Menu()
		self.menu3_aide = Gtk.MenuItem("Aide")
		
		self.charger_galaxies_tab = Gtk.MenuItem("Charger Galaxies Tableau")
		self.menu1.append(self.charger_galaxies_tab)
		self.charger_galaxies_tab.connect('activate', self.charger_tableau)

		self.menu1.append(Gtk.SeparatorMenuItem())
		self.save_graphe = Gtk.MenuItem("Sauvegarder Graphe")
		self.menu1.append(self.save_graphe)
		self.save_graphe.connect('activate', self.save)
		self.menu1.append(Gtk.SeparatorMenuItem())
		self.exit = Gtk.MenuItem("Exit")
		self.exit.connect('activate', Gtk.main_quit)
		self.menu1.append(self.exit)	
		self.filtre_auteur = Gtk.MenuItem("Filtrer Galaxies selon Auteur")
		self.filtre_auteur.connect('activate', lambda x=0, y=0: self.filtre_galaxies(x, y))
		self.menu2.append(self.filtre_auteur)
		self.filtre_annee = Gtk.MenuItem("Filtrer Galaxies selon Année")
		self.filtre_annee.connect('activate', lambda x=0, y=1 : self.filtre_galaxies(x, y))
		self.menu2.append(self.filtre_annee)
		self.menu2.append(Gtk.SeparatorMenuItem())
		self.filtre_auteur2 = Gtk.MenuItem("Filtrer Graphe selon Auteur")
		self.filtre_auteur2.connect('activate', lambda x=0, y=0: self.filtre_graphe(x, y))
		self.menu2.append(self.filtre_auteur2)
		self.filtre_annee2 = Gtk.MenuItem("Filtrer Graphe selon Année")
		self.filtre_annee2.connect('activate', lambda x=0, y=1 : self.filtre_graphe(x, y))
		self.menu2.append(self.filtre_annee2)
		self.menu2.append(Gtk.SeparatorMenuItem())
		self.voir_supp = Gtk.MenuItem("Voir/Supprimer Filtres")
		self.voir_supp.connect('activate', self.supprimer_filtres_galaxies)
		self.menu2.append(self.voir_supp)

		
		self.menubar.append(self.menu1_file)
		self.menubar.append(self.menu2_filtre)
		self.menubar.append(self.menu3_aide)
		
		self.vbox = Gtk.VBox(False, 2)
		self.vbox.pack_start(self.menubar, False, False, 0)
		self.window.add(self.vbox)
		
		self.hbox = Gtk.HBox(False, 0)
		
		#barre horizontal
		self.sw = Gtk.VBox(False, 0)
		#barre vertical
		self.sw2 = Gtk.HBox(False, 0)
		

		######################################## Radio Button
		self.node_choice = Gtk.HBox(False, 0)
		self.label_info = Gtk.Label("Information des nœuds : ")
		self.radio_button_simple = Gtk.RadioButton("Aucune")
		self.radio_button_label = Gtk.RadioButton().new_from_widget(self.radio_button_simple)
		self.radio_button_reut = Gtk.RadioButton().new_from_widget(self.radio_button_simple)
		self.radio_button_titre = Gtk.RadioButton().new_from_widget(self.radio_button_simple)
		self.radio_button_auteur = Gtk.RadioButton().new_from_widget(self.radio_button_simple)
		self.radio_button_date = Gtk.RadioButton().new_from_widget(self.radio_button_simple)
		self.radio_button_label.set_label("Labels")
		self.radio_button_reut.set_label("Réutilisations")
		self.radio_button_titre.set_label("Titres")
		self.radio_button_auteur.set_label("Auteur")
		self.radio_button_date.set_label("Années")
		self.radio_button_simple.connect("toggled", self.radio_button_change, "6")
		self.radio_button_label.connect("toggled", self.radio_button_change, "0")
		self.radio_button_reut.connect("toggled", self.radio_button_change, "4")
		self.radio_button_titre.connect("toggled", self.radio_button_change, "1")
		self.radio_button_auteur.connect("toggled", self.radio_button_change, "2")
		self.radio_button_date.connect("toggled", self.radio_button_change, "3")

		self.radio_button_label.set_sensitive(False)
		self.radio_button_reut.set_sensitive(False)
		self.radio_button_titre.set_sensitive(False)
		self.radio_button_auteur.set_sensitive(False)
		self.radio_button_date.set_sensitive(False)

		self.node_choice.pack_start(self.label_info, False, False, 5)
		self.node_choice.pack_start(self.radio_button_simple, False, False, 5)
		self.node_choice.pack_start(self.radio_button_label, False, False, 5)
		self.node_choice.pack_start(self.radio_button_reut, False, False, 5)
		self.node_choice.pack_start(self.radio_button_titre, False, False, 5)
		self.node_choice.pack_start(self.radio_button_auteur, False, False, 5)
		self.node_choice.pack_start(self.radio_button_date, False, False, 5)

		#self.sw2.add(self.node_choice)
		#####################################################################

		self.vbox2 = Gtk.VBox(False, 2)

		self.g = Graph()

		position = sfdp_layout(self.g)
		self.l = GraphWidget(self.g, pos=position, vertex_font_size=15)
		self.window.connect("button-press-event", self.get_id_node)
		
		self.l.set_size_request(self.window.get_screen().get_width() -400, self.window.get_screen().get_height () -400)
		
		#self.sw.add_with_viewport(self.vbox2)
		
		self.hbox.pack_start(self.sw, True, True, 0)

		self.haut_droite = Gtk.VBox()
		self.haut_droite.pack_start(self.node_choice, False, False, 10)
		self.haut_droite.pack_start(self.l, True, True, 0)
		self.hbox.pack_start(self.haut_droite, True, True, 0)

		#self.hbox.pack_start(self.l, False, False, 0)

		
		self.vbox.add(self.hbox)
		self.vbox.add(self.sw2)
		
		self.window.connect("delete-event", Gtk.main_quit)
		self.window.show_all()
		
		Gtk.main()
      

	def message_dial(self, message):
		dialog = Gtk.Dialog(message, self.window, 0, (Gtk.STOCK_OK, Gtk.ResponseType.OK))
		v = dialog.get_content_area()
		v.pack_start(Gtk.Label(message), False, False, 0)
		dialog.show_all()
		response = dialog.run()
		if response == Gtk.ResponseType.OK:
			dialog.destroy()


	def save(self, event):		
		if self.path == None:
			return
		dialog = Gtk.FileChooserDialog("Save File", self.window,
            Gtk.FileChooserAction.SAVE,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OK, Gtk.ResponseType.OK))
		response = dialog.run()
		if response == Gtk.ResponseType.OK:
			position = sfdp_layout(self.g)
			graph_draw(self.g, pos=position, vertex_fill_color=self.property_vertex_color, vertex_size=self.property_vertex_size, output_size=(1920, 1080), output=dialog.get_filename()+".svg")
		dialog.destroy()


	def charger_tableau(self, event):
		dialog = Gtk.FileChooserDialog("Please choose a file", self.window,
            	 Gtk.FileChooserAction.OPEN,
            	 (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            	 Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
		response = dialog.run()
		if response == Gtk.ResponseType.OK:
			self.path = dialog.get_filename()
			rows = get_father_son(self.path)
			self.list_list_edges = [rows]
			dialog.destroy()
			self.tab_inside = GtkTabInside(self, self.path)
		else:
			dialog.destroy()



	def del_double(self):
		i = 0
		dico_label = dict()
		dico_titre = dict()
		dico_auteur = dict()
		dico_date = dict()
		dico_texte = dict()
		dico_pour_edges = dict()

		new_graph = Graph(directed=False)
		c = label_components(self.graphe)[0]
		for v in self.graphe.vertices():
			if c[v] == 0:
				v1 = new_graph.add_vertex()
				v_id = self.graphe.vertex_index[v]
				label = self.tab_donnees[0][v_id]
				l = self.tab_donnees[5][label]
				dico_pour_edges[v_id] = i
				if l[0] == v_id:
					v_equiv = l[1]
				else:
					v_equiv = l[0]

				dico_label[i] = label
				try: dico_titre[i] = self.tab_donnees[1][v_id]
				except: dico_titre[i] = self.tab_donnees[1][v_equiv]
				try: dico_auteur[i] = self.tab_donnees[2][v_id]
				except: dico_auteur[i] = self.tab_donnees[2][v_equiv]
				try: dico_date[i]  = self.tab_donnees[3][v_id]
				except: dico_date[i]  = self.tab_donnees[3][v_equiv]
				try: dico_texte[i] = self.tab_donnees[4][v_id]
				except: dico_texte[i] = self.tab_donnees[4][v_equiv]
				i += 1
		for e in self.graphe.get_edges():
			if e[0] in dico_pour_edges:
				new_graph.add_edge(dico_pour_edges[e[0]], dico_pour_edges[e[1]])

		self.graphe = new_graph
		self.tab_donnees = [dico_label, dico_titre, dico_auteur, dico_date, dico_texte]

		#g = GraphView(self.graphe, vfilt=c.a == 0)
		#self.graphe = Graph(g, prune=True)


	def taille_couleur_noeuds(self):
		v_iterator = self.graphe.vertices()
		n = self.graphe.num_vertices()
		self.property_vertex_couleur = self.graphe.new_vertex_property("string")
		self.property_vertex_taille  = self.graphe.new_vertex_property("int32_t")
		for v in v_iterator:
			deg = v.out_degree()
			if deg > n/5:
				self.property_vertex_couleur[v] = "black"
				self.property_vertex_taille[v] = 20
			elif deg > n/7:
				self.property_vertex_couleur[v] = "gray"
				self.property_vertex_taille[v] = 15
			else:
				self.property_vertex_couleur[v] = "turquoise"
				self.property_vertex_taille[v] = 10



	def display_galaxie(self, galaxie_id):
		self.galaxie_id = galaxie_id
		self.initialise_data_from_nx()
		self.graphe = load_graph("results/galaxies/graphe_galaxie_" + str(galaxie_id) + ".gml")
		self.l.destroy()
		self.del_double()
		self.node_to_data()
		self.taille_couleur_noeuds()
		position = sfdp_layout(self.graphe)
		self.l = GraphWidget(self.graphe, pos=position, display_props=self.property_label_plus_texte, vertex_fill_color=self.property_vertex_couleur, vertex_size=self.property_vertex_taille)
		self.l.set_size_request(self.window.get_screen().get_width() -400, self.window.get_screen().get_height () -400)
		
		self.haut_droite.pack_start(self.l, True, True, 0)
		self.tableau = GtkTabBas(self, self.tab_donnees)
		self.radio_button_simple.set_active(True)
		self.radio_button_label.set_sensitive(True)
		self.radio_button_reut.set_sensitive(True)
		self.radio_button_titre.set_sensitive(True)
		self.radio_button_auteur.set_sensitive(True)
		self.radio_button_date.set_sensitive(True)
		self.graphe_copie = Graph(self.graphe)
		self.list_filter_graph = []
		self.noeud_filtre_ne_pas_supprimer = []
		self.noeud_filtre_a_supprimer = []
		self.already_filter_author = False
		self.already_filter_date = False
		self.window.show_all()
	
	def initialise_data_from_nx(self):
		self.tab_donnees = []
		G = nx.read_gml("results/galaxies/graphe_galaxie_" + str(self.galaxie_id) + ".gml", label="id")	
		self.tab_donnees.append(nx.get_node_attributes(G,'label'))
		self.tab_donnees.append(nx.get_node_attributes(G,'titre'))
		self.tab_donnees.append(nx.get_node_attributes(G,'auteur'))
		self.tab_donnees.append(nx.get_node_attributes(G,'date'))
		self.tab_donnees.append(nx.get_node_attributes(G,'texte'))
		self.tab_donnees.append(get_equivalent(self.tab_donnees[0]))


	def get_id_node(self, widget, event):
		id_node = self.l.picked
		if self.galaxie_id != None:
			v = self.graphe.vertex(id_node)
			sel = None
			label = self.property_vertex_label[v]
			for row in self.tableau.store:
				sel = row
				if label == row[0]:
					break

			self.tableau.store.swap(row.iter, self.tableau.store[0].iter)
			self.window.show_all()


	def node_to_data(self):
		self.property_vertex_label  = self.graphe.new_vertex_property("string")
		self.property_vertex_titre  = self.graphe.new_vertex_property("string")
		self.property_vertex_auteur = self.graphe.new_vertex_property("string")
		self.property_vertex_date   = self.graphe.new_vertex_property("int32_t")
		self.property_vertex_texte  = self.graphe.new_vertex_property("string")
		self.property_label_plus_texte = self.graphe.new_vertex_property("string")

		for v in self.graphe.vertices():
			node_id = self.graphe.vertex_index[v]
			self.property_vertex_label[v] = self.tab_donnees[0][node_id]
			self.property_vertex_titre[v] = self.tab_donnees[1][node_id]
			self.property_vertex_auteur[v] = self.tab_donnees[2][node_id]
			self.property_vertex_date[v] = self.tab_donnees[3][node_id]	
			self.property_vertex_texte[v] = self.tab_donnees[4][node_id]
			self.property_label_plus_texte[v] = self.tab_donnees[0][node_id]\
			+ " : " + self.tab_donnees[4][node_id]


	def radio_button_change(self, button, num):
		self.l.destroy()
		position = sfdp_layout(self.graphe)
		if num == "0":
			self.l = GraphWidget(self.graphe, pos=position, vertex_text=self.property_vertex_label, display_props=self.property_label_plus_texte, vertex_fill_color=self.property_vertex_couleur, vertex_size=self.property_vertex_taille)
		elif num == "1":
			self.l = GraphWidget(self.graphe, pos=position, vertex_text=self.property_vertex_titre, display_props=self.property_label_plus_texte, vertex_fill_color=self.property_vertex_couleur, vertex_size=self.property_vertex_taille)
		elif num == "2":
			self.l = GraphWidget(self.graphe, pos=position, vertex_text=self.property_vertex_auteur, display_props=self.property_label_plus_texte, vertex_fill_color=self.property_vertex_couleur, vertex_size=self.property_vertex_taille)
		elif num == "3":
			self.l = GraphWidget(self.graphe, pos=position, vertex_text=self.property_vertex_date, display_props=self.property_label_plus_texte, vertex_fill_color=self.property_vertex_couleur, vertex_size=self.property_vertex_taille)
		elif num == "4":
			self.l = GraphWidget(self.graphe, pos=position, vertex_text=self.property_vertex_texte, display_props=self.property_label_plus_texte, vertex_fill_color=self.property_vertex_couleur, vertex_size=self.property_vertex_taille)
		elif num == "6":
			self.l = GraphWidget(self.graphe, pos=position, display_props=self.property_label_plus_texte, vertex_fill_color=self.property_vertex_couleur, vertex_size=self.property_vertex_taille)
		
		self.l.set_size_request(self.window.get_screen().get_width() -400, self.window.get_screen().get_height () -400)
		self.haut_droite.pack_start(self.l, True, True, 0)
		self.window.show_all()

	def liste_noeuds_filtre(self, type_filtre, filtre, inv):
		nbr = len(os.listdir("results/galaxies")) - 1
		liste_id = []
		for i in range(nbr):
			G = nx.read_gml("results/galaxies/graphe_galaxie_" + str(i) + ".gml", label="id")
			dico = nx.get_node_attributes(G, type_filtre)
			liste = list(dico.values())
			if not inv:
				if filtre not in liste:
					liste_id.append(i)
			else:
				if filtre in liste:
					liste_id.append(i)
		return liste_id


	def filtre_galaxies(self, event, choix):
		if self.path is not None:
			author, date = get_authors_date(self.path)
			dialog = Gtk.Dialog("Filtre", self.window, 0, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK))
			v = dialog.get_content_area()
			
			if choix == 0:
				type_filter = "auteur"
				liste = Gtk.ListStore(str)
				for i in author:
					liste.append([i[0]])
			else:
				type_filter = "date"
				liste = Gtk.ListStore(int)
				for i in date:
					liste.append([i[0]])
						
			cb = Gtk.ComboBox().new_with_model(liste)
			rt = Gtk.CellRendererText()
			cb.pack_start(rt, True)		
			cb.add_attribute(rt, "text", 0)
			
			check_b = Gtk.CheckButton("Inverser")
			v.pack_start(cb, False, False, 0)
			v.pack_start(check_b, False, False, 0)
			
			dialog.show_all()
			response = dialog.run()
			if response == Gtk.ResponseType.OK:
				i = cb.get_active_iter()
				if i is not None:
					if check_b.get_active():
						inv = "inversé "
					else:
						inv = " "

					if  ((type_filter == "auteur" and self.already_filter_author) or (type_filter == "année" and self.already_filter_date)):
						self.message_dial("Filtre " + type_filter +" déjà existant, veuillez le supprimer")
						dialog.destroy()
						return
				
					fil = cb.get_model()[i][0]

					############################################################################
					liste_id = self.liste_noeuds_filtre(type_filter, fil, check_b.get_active())
					if len(liste_id) == 0:
						self.message_dial("Aucun résultat")
						dialog.destroy()
						return

					self.tab_inside.filtre(liste_id)
					
			dialog.destroy()





	def filtre_graphe(self, event, choix):
		dialog = Gtk.Dialog("Filtre", self.window, 0, (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OK, Gtk.ResponseType.OK))
		v = dialog.get_content_area()
			
		if choix == 0:
			type_filter = "auteur"
			liste = Gtk.ListStore(str)
			for auteur in set(list(self.tab_donnees[2].values())):
				liste.append([auteur])
		else:
			type_filter = "date"
			liste = Gtk.ListStore(int)
			for date in set(list(self.tab_donnees[3].values())):
				liste.append([date])
						
		cb = Gtk.ComboBox().new_with_model(liste)
		rt = Gtk.CellRendererText()
		cb.pack_start(rt, True)		
		cb.add_attribute(rt, "text", 0)
			
		check_b = Gtk.CheckButton("Inverser")
		v.pack_start(cb, False, False, 0)
		v.pack_start(check_b, False, False, 0)
			
		dialog.show_all()
		response = dialog.run()
		if response == Gtk.ResponseType.OK:
			i = cb.get_active_iter()
			if i is not None:
				if check_b.get_active():
					inv = "inversé "
				else:
					inv = " "

				if  ((type_filter == "auteur" and self.already_filter_author) or (type_filter == "année" and self.already_filter_date)):
					self.message_dial("Un filtre " + type_filter +" non inversé existe  déjà, veuillez le supprimer")
					dialog.destroy()
					return
				
				fil = cb.get_model()[i][0]
				check = check_b.get_active()
				self.noeud_pour_graphe_filtre(fil, type_filter, check)

		dialog.destroy()
		self.tableau.filtre()
		self.window.show_all()

	
	def noeud_pour_graphe_filtre(self, filtre, type_fil, inv_coche):
		not_del = []
		if type_fil == "auteur":
			donnees = self.property_vertex_auteur
			if not inv_coche:
				self.already_filter_author = True
		else:
			donnees = self.property_vertex_date
			if not inv_coche:
				self.already_filter_date = True
	
		for e in self.graphe.get_edges():
			e_0 = donnees[e[0]]
			e_1 = donnees[e[1]]

			if not inv_coche:
				if e_0 == filtre or e_1 == filtre:
					not_del.append(e[0])
					not_del.append(e[1])
			else:
				if e_0 != filtre and e_1 != filtre:
					not_del.append(e[0])
					not_del.append(e[1])

		self.noeud_filtre_ne_pas_supprimer.append(not_del)
		self.list_filter_graph.append([type_fil, filtre , inv_coche])
		v2del = []
		for v in self.graphe.vertices():
			if self.graphe.vertex_index[v] not in intersection(self.noeud_filtre_ne_pas_supprimer):
				v2del.append(v)

		self.noeud_filtre_a_supprimer.append(v2del)
		if len(v2del) == 1:
			v2del = v2del[0]
		self.graphe.remove_vertex(v2del)

		self.l.destroy()
		position = sfdp_layout(self.graphe)
		self.l = GraphWidget(self.graphe, pos=position, display_props=self.property_label_plus_texte, vertex_fill_color=self.property_vertex_couleur, vertex_size=self.property_vertex_taille)
		self.l.set_size_request(self.window.get_screen().get_width() -400, self.window.get_screen().get_height () -400)
		self.haut_droite.pack_start(self.l, True, True, 0)
		self.window.show_all()


	def supprimer_filtres_galaxies(self, event):
		GtkTabFiltre(self)

if __name__ == "__main__":
	menu = WindowsGalaxieVizualisation()

