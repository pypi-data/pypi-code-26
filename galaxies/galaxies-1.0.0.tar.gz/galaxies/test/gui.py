import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
from graph_tool.all import *


class Gui:
    def __init__(self):
        self.window = Gtk.Window(title="Test")
        # self.window.set_size_request(500, 500)
        # self.window.set_position(Gtk.WIN_POS_CENTER)

        # self.grid = Gtk.Grid()

        self.menubar = Gtk.MenuBar()

        self.menu1 = Gtk.Menu()
        self.menu1_file = Gtk.MenuItem("Fichier")
        self.menu1_file.set_submenu(self.menu1)

        self.menu2 = Gtk.Menu()
        self.menu2_filtre = Gtk.MenuItem("Filtre")
        self.menu2_filtre.set_submenu(self.menu2)

        self.menu3 = Gtk.Menu()
        self.menu3_aide = Gtk.MenuItem("Aide")
        self.menu3_aide.set_submenu(self.menu2)

        self.charger_reutilisation = Gtk.MenuItem("Charger Réutilisation")
        self.menu1.append(self.charger_reutilisation)
        self.charger_graphe = Gtk.MenuItem("Charger Graphe")
        self.menu1.append(self.charger_graphe)
        self.menu1.append(Gtk.SeparatorMenuItem())
        self.save_graphe = Gtk.MenuItem("Sauvegarder Graphe")
        self.menu1.append(self.save_graphe)
        self.menu1.append(Gtk.SeparatorMenuItem())
        self.exit = Gtk.MenuItem("Exit")
        self.menu1.append(self.exit)

        self.filtre_auteur = Gtk.MenuItem("Filtrer Auteur")
        self.menu2.append(self.filtre_auteur)
        self.filtre_annee = Gtk.MenuItem("Filtrer Année")
        self.menu2.append(self.filtre_annee)

        self.menubar.append(self.menu1_file)
        self.menubar.append(self.menu2_filtre)
        self.menubar.append(self.menu3_aide)

        self.vbox = Gtk.VBox(False, 2)
        self.vbox.pack_start(self.menubar, False, False, 0)
        self.window.add(self.vbox)

        self.hbox = Gtk.HBox(False, 0)

        self.sw = Gtk.ScrolledWindow()
        self.sw2 = Gtk.ScrolledWindow()

        self.vbox2 = Gtk.VBox(False, 2)

        self.but = Gtk.Button(label="Filtre 1\nFiltre Auteur: Shakespear")
        self.but2 = Gtk.Button(label="Filtre 2\nFiltre Auteur: Flaubert")
        self.but3 = Gtk.Button(label="Filtre 3\nFiltre Auteur: Maupassant")

        self.but4 = Gtk.Button(label="Filtre 3\nFiltre Auteur: Shakespear")
        self.but5 = Gtk.Button(label="Filtre 4\nFiltre Auteur: Flaubert")
        self.but6 = Gtk.Button(label="Filtre 5\nFiltre Auteur: Maupassant")

        self.but7 = Gtk.Button(label="Filtre 6\nFiltre Auteur: Shakespear")
        self.but8 = Gtk.Button(label="Filtre 7\nFiltre Auteur: Flaubert")
        self.but9 = Gtk.Button(label="Filtre 8\nFiltre Auteur: Maupassant")

        self.label = Gtk.Label(
            label="BlablablablaBlablablablaBlablablablaBlablablablaBlablablablaBlablablablaBlablablablaBlablablablaBlablabl\nablaBlablablablaBlablablablaBlablablablaBlablablablaBlablablablaBlablablablaBlablablablaBlablablablaBlablablablaBlablablablaBlablablabla\nBlablablablaBlablablablaBlablablablaBlablablablaBlablablablaBlablablablaBlablablablaBlablablablaBlablablablaBlablablablaBlablablablaBlablablabla")

        self.sw.set_size_request(200, 500)
        self.sw2.set_size_request(200, 150)

        g = Graph()
        v1 = g.add_vertex()
        v2 = g.add_vertex()
        v3 = g.add_vertex()
        v4 = g.add_vertex()
        v5 = g.add_vertex()
        v6 = g.add_vertex()
        e1 = g.add_edge(v1, v2)
        e2 = g.add_edge(v2, v3)
        e3 = g.add_edge(v1, v3)
        e4 = g.add_edge(v1, v5)
        e5 = g.add_edge(v2, v4)
        e6 = g.add_edge(v1, v6)

        position = sfdp_layout(g)
        l = GraphWidget(g, pos=position, vertex_text=g.vertex_index,
                        vertex_font_size=15)
        l.set_size_request(600, 500)
        self.vbox2.pack_start(self.but, False, True, 5)
        self.vbox2.pack_start(self.but2, False, True, 5)
        self.vbox2.pack_start(self.but3, False, True, 5)

        self.vbox2.pack_start(self.but4, False, True, 5)
        self.vbox2.pack_start(self.but5, False, True, 5)
        self.vbox2.pack_start(self.but6, False, True, 5)

        self.vbox2.pack_start(self.but7, False, True, 5)
        self.vbox2.pack_start(self.but8, False, True, 5)
        self.vbox2.pack_start(self.but9, False, True, 5)

        self.sw.add_with_viewport(self.vbox2)
        self.hbox.pack_start(self.sw, True, True, 0)
        self.hbox.pack_start(l, False, False, 0)

        color = Gdk.color_parse('#d3d3d3')
        color2 = Gdk.color_parse('#595959')
        self.sw.modify_bg(Gtk.StateType.NORMAL, color)
        self.sw2.modify_bg(Gtk.StateType.NORMAL, color)
        self.sw2.add_with_viewport(self.label)
        self.vbox.add(self.hbox)
        self.vbox.add(self.sw2)

        self.window.connect("delete-event", Gtk.main_quit)
        self.window.show_all()
        Gtk.main()


gui = Gui()
