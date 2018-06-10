import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from graph_tool.all import *




class TestWindow(Gtk.Window):
	def __init__(self):
			Gtk.Window.__init__(self, title="Test")
			self.resize(800, 600)
			#self.button = Gtk.Button(label="Display fucking graph")
			#self.button.connect("clicked", self.on_button_clicked)
			#self.add(self.button)
			
	#def on_button_clicked(self, widget):
			g = Graph()
			v1 = g.add_vertex()
			v2 = g.add_vertex()
			e = g.add_edge(v1, v2)
			
			
			nb = Gtk.Notebook()
			self.add(nb)
			
			page1 = Gtk.Box()
			nb.append_page(page1, Gtk.Label("Page 1"))
			
			
			
			position = sfdp_layout(g)
			l = GraphWidget(g, pos=position)
			
			nb.append_page(l, Gtk.Label("Graph"))
			
			#grid = Gtk.Grid()
			
			#self.add(l2)
			#grid.add(l)
			
			
class TestWindow2(Gtk.Window):
	def __init__(self):
			Gtk.Window.__init__(self, title="Test")
			self.resize(800, 600)
			
			self.grid = Gtk.Grid()
			self.add(self.grid)
			
			self.button = Gtk.Button(label="Display fucking graph")
			self.button.connect("clicked", self.on_button_clicked)
			self.grid.add(self.button)
			
	def on_button_clicked(self, widget):
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
			l = GraphWidget(g, pos=position, vertex_text=g.vertex_index, vertex_font_size=15)
			l.set_size_request(400,400)
			self.grid.attach(l, 0, 1, 5, 5)
			window.show_all()
			#grid.add(l)
			
window = TestWindow2()
window.connect("delete-event", Gtk.main_quit)
window.show_all()
Gtk.main()
