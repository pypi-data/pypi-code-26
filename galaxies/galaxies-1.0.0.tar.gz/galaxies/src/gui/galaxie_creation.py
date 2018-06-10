""" This modules contains all functions, methods and classes related to GUI. """
from tkinter.filedialog import *
from tkinter.messagebox import *

import galaxies.src.core.environment as env
from galaxies.src.core.interface import create_reuses_database, impressionTexteEtReferenceLongueurGUI

# Theme-related variables
DARK = 0
GRAY = 1
TURQUOISE = 2
BLUE = 3
THEMES = {
    DARK: {
        "BG_BUTTON": '#%02x%02x%02x' % (94, 94, 94),
        "BG_FRAME": '#%02x%02x%02x' % (68, 68, 68),
        "BG_ENTRY": '#%02x%02x%02x' % (42, 42, 42),
        "FG_COLOR": "white"
    },
    GRAY: {
        "BG_BUTTON": '#%02x%02x%02x' % (240, 240, 240),
        "BG_FRAME": '#%02x%02x%02x' % (240, 240, 240),
        "BG_ENTRY": "white",
        "FG_COLOR": "black"
    },
    TURQUOISE: {
        "BG_BUTTON": '#%02x%02x%02x' % (1, 133, 134),
        "BG_FRAME": '#%02x%02x%02x' % (1, 133, 134),
        "BG_ENTRY": '#%02x%02x%02x' % (0, 86, 87),
        "FG_COLOR": "white"
    },
    BLUE: {
        "BG_BUTTON": '#%02x%02x%02x' % (0, 169, 232),
        "BG_FRAME": '#%02x%02x%02x' % (0, 169, 232),
        "BG_ENTRY": '#%02x%02x%02x' % (199, 224, 255),
        "FG_COLOR": '#%02x%02x%02x' % (11, 38, 75)
    }
}

# Messages-related variables
MESSAGE_ERROR_FORMAT = "Formats currently supported are : {}."
MESSAGE_ERROR_NO_SOURCE_FILE = "No reuses' file chosen."

LISTE_PARAM1 = [env.index_src_author, env.index_src_title, env.index_src_date,
                env.index_src_text_matched, env.index_src_start_byte,
                env.index_src_end_byte, env.index_dest_author, env.index_dest_title,
                env.index_dest_date, env.index_dest_text_matched, env.index_dest_start_byte,
                env.index_dest_end_byte]
LISTE_PARAM2 = [env.step_nodes_time, env.step_galaxies_time, env.step_number_of_nodes_galaxie]

POSSIBLES_EXTENSIONS = ("tsv", "tab", "csv", "json")
EXTENSIONS_DB_REUSES = [('json files', '.json'),
                        ('tsv files', '.tsv'),
                        ('tab files', '.tab'),
                        ('csv files', '.csv'),
                        ('all files', '.*')]
EXTENSIONS_GALAXIE = [('db files', '.db'),
                      ('all files', '.*')]


class WindowsGalaxieCreation:
    def __init__(self, theme=GRAY):
        self.BG_BUTTON = None
        self.BG_FRAME = None
        self.BG_ENTRY = None
        self.FG_COLOR = None
        self._set_colors(theme)

        # Création de la fenêtre
        self.window = Tk()
        self.window_frame = Frame(self.window, bg=self.BG_FRAME)
        self.window.resizable(False, False)
        self.window_frame.grid()
        self.window_frame.rowconfigure(0, weight=1)
        self.window_frame.columnconfigure(0, weight=1)

        self.all_button = []
        self.all_entry = []
        self.all_label = []
        self.all_frame = []

        self.run_already = False

        self._place_menu_bar()
        self._create_bindings()
        self.panel_create()

        self.window.mainloop()

    def panel_open_database(self, event=None):
        self.clear_frame(self.window_frame)
        self.position = 1
        path = askopenfilename(title="Open", filetypes=EXTENSIONS_DB_REUSES)
        if path == "":
            self.panel_create()
        if path[-3:] in POSSIBLES_EXTENSIONS:
            with open(path, 'r') as T:
                self.liste_line = [next(T) for i in range(100)]
            header = self.liste_line[0]
            text = self.liste_line[1]

            self.label_head = Label(self.window_frame, text="Header", bg=self.BG_FRAME, fg=self.FG_COLOR)
            self.all_label.append(self.label_head)
            self.header = Text(self.window_frame, width=100, height=6, bg=self.BG_ENTRY, fg=self.FG_COLOR)
            self.all_entry.append(self.header)
            self.label_text = Label(self.window_frame, text="File", bg=self.BG_FRAME, fg=self.FG_COLOR)
            self.all_label.append(self.label_text)
            self.text = Text(self.window_frame, width=100, height=15, bg=self.BG_ENTRY, fg=self.FG_COLOR)
            self.all_entry.append(self.text)

            self.previous_button = Button(self.window_frame, text="Prev", bg=self.BG_BUTTON, fg=self.FG_COLOR,
                                          state=DISABLED, command=lambda x=-1: self.next_previous(x))
            self.next_button = Button(self.window_frame, text="Next", bg=self.BG_BUTTON, fg=self.FG_COLOR,
                                      command=lambda x=1: self.next_previous(x))
            self.create_button = Button(self.window_frame, text="Create database", bg=self.BG_BUTTON, fg=self.FG_COLOR,
                                        command=self.create_reuses_database)

            self.all_button.append(self.previous_button)
            self.all_button.append(self.next_button)
            self.all_button.append(self.create_button)

            self.header.insert(1.0, header)
            self.text.insert(1.0, text)

            self.label_head.grid(row=1, column=1, columnspan=2)
            self.header.grid(row=2, column=1, columnspan=2)
            self.label_text.grid(row=3, column=1, columnspan=2)
            self.text.grid(row=4, column=1, columnspan=2)
            self.previous_button.grid(row=5, column=1, sticky=E)
            self.next_button.grid(row=5, column=2, sticky=W)
            self.create_button.grid(row=6, column=1, columnspan=2, pady=15)
        else:
            showerror("Error", "Only tsv file")
            self.panel_create()

    def next_previous(self, n):
        self.position += n
        if self.position == 1:
            self.previous_button.config(state=DISABLED)
        elif self.position == 2:
            self.previous_button.config(state=NORMAL)
        elif self.position == 99:
            self.next_button.config(state=DISABLED)
        elif self.position == 98 and n == -1:
            self.next_button.config(state=NORMAL)

        self.text.delete('1.0', END)
        self.text.insert(1.0, self.liste_line[self.position])

    def panel_create(self, event=None, option=True):
        self.clear_frame(self.window_frame)
        self.path_open = StringVar()
        self.path_save = StringVar()
        self.create_frame = LabelFrame(self.window_frame, text="Create Database", bg=self.BG_FRAME, fg=self.FG_COLOR)
        self.all_frame.append(self.create_frame)
        self.create_frame.grid(row=1, padx=5, pady=5)
        self.button_open = Button(self.create_frame, text=" Open  ", bg=self.BG_BUTTON, fg=self.FG_COLOR,
                                  command=self.open_reuses_database)
        self.all_button.append(self.button_open)
        self.entry_open = Entry(self.create_frame, textvariable=self.path_open, width=30, bg=self.BG_ENTRY,
                                fg=self.FG_COLOR)
        # self.entry_save_as = Entry(self.create_frame, textvariable=self.path_save, width=30, bg=self.BG_ENTRY, fg=self.FG_COLOR)
        self.all_entry.append(self.entry_open)
        # self.all_entry.append(self.entry_save_as)
        # self.button_save_as = Button(self.create_frame, text="Save as", bg=self.BG_BUTTON, fg=self.FG_COLOR, command=self.save_create)
        self.button_create = Button(self.create_frame, text="Create", bg=self.BG_BUTTON, fg=self.FG_COLOR,
                                    command=self.create_reuses_database)
        # self.all_button.append(self.button_save_as)
        self.all_button.append(self.button_create)

        self.button_open.grid(row=1, column=1, padx=(5, 0), pady=5)
        self.entry_open.grid(row=1, column=2, padx=(0, 5), pady=5)
        # self.button_save_as.grid(row=2, column=1, padx=(5,0), pady=5)
        # self.entry_save_as.grid(row=2, column=2, padx=(0,5), pady=5)
        self.button_create.grid(row=3, column=1, columnspan=2, padx=5, pady=5)

        if option:
            self.panel_run()

    def panel_run(self, event=None, row=8):
        self.run_frame = LabelFrame(self.window_frame, text="Run",
                                    bg=self.BG_FRAME, fg=self.FG_COLOR)
        self.button_open2 = Button(self.run_frame, text=" Open  ",
                                   bg=self.BG_BUTTON, fg=self.FG_COLOR, command=self.open_galaxies_database)
        self.path_database = StringVar()
        self.entry_open2 = Entry(self.run_frame,
                                 textvariable=self.path_database, width=30,
                                 bg=self.BG_ENTRY, fg=self.FG_COLOR)
        self.button_run = Button(self.run_frame, text="Run",
                                 bg=self.BG_BUTTON, fg=self.FG_COLOR, command=self.run)

        self.label_n = Label(self.run_frame, text="n", bg=self.BG_FRAME, fg=self.FG_COLOR)
        self.all_label.append(self.label_n)
        self.label_p = Label(self.run_frame, text="p", bg=self.BG_FRAME, fg=self.FG_COLOR)
        self.all_label.append(self.label_p)
        self.spin_n = Spinbox(self.run_frame, width=5, bg=self.BG_ENTRY, fg=self.FG_COLOR, insertbackground="white",
                              buttonbackground=self.BG_BUTTON)
        self.spin_p = Spinbox(self.run_frame, width=5, bg=self.BG_ENTRY, fg=self.FG_COLOR, insertbackground="white",
                              buttonbackground=self.BG_BUTTON)
        self.all_spin = [self.spin_n, self.spin_p]

        self.run_frame.grid(row=row, columnspan=3, padx=5, pady=5)
        self.button_open2.grid(row=1, column=1, padx=(5, 0), pady=5)
        self.entry_open2.grid(row=1, column=2, columnspan=3, padx=(0, 5), pady=5)
        self.button_run.grid(row=3, column=1, columnspan=4, padx=5, pady=5)

        self.label_n.grid(row=2, column=1, padx=(0, 5), sticky=E)
        self.label_p.grid(row=2, column=3, padx=(0, 5), sticky=E)
        self.spin_n.grid(row=2, column=2, pady=(0, 10), sticky=W)
        self.spin_p.grid(row=2, column=4, pady=(0, 10), sticky=W)

        self.run_frame_2 = Frame(self.run_frame, bg=self.BG_FRAME)
        self.run_frame_2.grid(row=2)
        self.all_frame.append(self.run_frame)
        self.all_frame.append(self.run_frame_2)
        self.all_button.append(self.button_open2)
        self.all_button.append(self.button_run)
        self.all_entry.append(self.entry_open2)

    def panel_edit_parameters(self, event=None, option=2):
        self.parameters_window = Tk()
        self.parameters_window.title("Edit Parameters")
        self.parameters_window.resizable(width=False, height=False)
        self.parameters_window.config(bg=self.BG_FRAME)
        self.header_frame = LabelFrame(self.parameters_window,
                                       text="Header Parameters",
                                       bg=self.BG_FRAME, fg=self.FG_COLOR)
        self.step_frame = LabelFrame(self.parameters_window,
                                     text="Step Parameters", bg=self.BG_FRAME,
                                     fg=self.FG_COLOR)

        self.all_frame.append(self.header_frame)
        self.all_frame.append(self.step_frame)

        self.save_button = Button(self.parameters_window, text="Save",
                                  bg=self.BG_BUTTON, fg=self.FG_COLOR, command=lambda x=option: self.save_param(x))
        self.save_button.grid(row=3, pady=5)

        self.all_button.append(self.save_button)

        tab_string1 = ["Source Author", "Source Title", "Source Date",
                       "Source Match", "Source Start Byte",
                       "Source End Byte", "Source End Byte",
                       "Target Title", "Target Date", "Target Match",
                       "Target Start Byte", "Target End Byte"]

        tab_string2 = ["Step Number Node",
                       "Step Galaxies", "Step Number Nodes Galaxie"]

        self.list_label_header = [Label(self.header_frame, text=label, bg=self.BG_FRAME, fg=self.FG_COLOR) for label in
                                  tab_string1]
        self.list_spin_header = [
            Spinbox(self.header_frame, width=5, bg=self.BG_ENTRY, fg=self.FG_COLOR, insertbackground="white",
                    buttonbackground=self.BG_BUTTON) for _ in tab_string1]
        self.list_label_step = [Label(self.step_frame, text=label, bg=self.BG_FRAME, fg=self.FG_COLOR) for label in
                                tab_string2]
        self.list_spin_step = [
            Spinbox(self.step_frame, width=10, bg=self.BG_ENTRY, fg=self.FG_COLOR, insertbackground="white",
                    buttonbackground=self.BG_BUTTON) for _ in tab_string2]

        for i in range(len(tab_string1)):
            if i < len(LISTE_PARAM2):
                self.list_spin_step[i].insert(0, LISTE_PARAM2[i])
            self.list_spin_header[i].insert(0, LISTE_PARAM1[i])

        for label in self.list_label_header:
            self.all_label.append(label)

        for label in self.list_label_step:
            self.all_label.append(label)

        if option in [0, 2]:
            self.place_frame(self.header_frame, 1, self.list_label_header,
                             self.list_spin_header, 3)

        if option in [1, 2]:
            self.place_frame(self.step_frame, 2, self.list_label_step,
                             self.list_spin_step, 2)

        self.parameters_window.mainloop()

    def save_param(self, option):
        try:
            if option in [0, 2]:
                sourceAuthor = int(self.list_spin_header[0].get())
                sourceTitle = int(self.list_spin_header[1].get())
                sourceDate = int(self.list_spin_header[2].get())
                sourceMatch = int(self.list_spin_header[3].get())
                sourceStartByte = int(self.list_spin_header[4].get())
                sourceEndByte = int(self.list_spin_header[5].get())
                targetAuthor = int(self.list_spin_header[6].get())
                targetTitle = int(self.list_spin_header[7].get())
                targetDate = int(self.list_spin_header[8].get())
                targetMatch = int(self.list_spin_header[9].get())
                targetStartByte = int(self.list_spin_header[10].get())
                targetEndByte = int(self.list_spin_header[11].get())

            if option in [1, 2]:
                pasTracage = int(self.list_spin_step[0].get())
                pasNbreNoeud = int(self.list_spin_step[1].get())
                pasGalaxies = int(self.list_spin_step[2].get())
                pasNbreNoeudsGalaxie = int(self.list_spin_step[3].get())

            self.parameters_window.destroy()
        except:
            showerror("Error", "Only integers")

    def place_frame(self, frame, row_frame, list_label, list_spin, n_column):
        frame.grid(row=row_frame, padx=5, pady=5)
        row = 1
        column = 1
        for i in range(len(list_label)):
            if i % n_column == 0:
                row += 1
                column = 1

            list_label[i].grid(row=row, column=column, padx=(0, 5), sticky=W)
            list_spin[i].grid(row=row, column=column + 1, padx=(0, 5),
                              pady=(0, 2), sticky=E)
            column += 2

    def clear_frame(self, frame):
        for widget in frame.winfo_children():
            if widget in self.all_frame:
                self.all_frame.remove(widget)
            elif widget in self.all_button:
                self.all_button.remove(widget)
            elif widget in self.all_entry:
                self.all_entry.remove(widget)
            elif widget in self.all_label:
                self.all_label.remove(widget)
            widget.destroy()

    def change_theme(self, theme):
        """ Change the theme of the Window.
        First, it change the attributes containing the colors of the window,
        then it reload all its components to set the new colors.
        """
        self._set_colors(theme)
        self._reload_colors()

    def _set_colors(self, theme):
        """ Change the attributes containing the colors of the window. """
        for name, color in zip(THEMES[theme].keys(), THEMES[theme].values()):
            setattr(self, name, color)

    def _reload_colors(self):
        """ Reload all the components of the windows with their the new color.
        """
        self.window_frame.config(bg=self.BG_FRAME)
        self.menu_bar.config(bg=self.BG_ENTRY)
        for button in self.all_button:
            try:
                button.config(bg=self.BG_BUTTON, fg=self.FG_COLOR)
            except:
                pass
        for entry in self.all_entry:
            try:
                entry.config(bg=self.BG_ENTRY, fg=self.FG_COLOR)
            except:
                pass
        for frame in self.all_frame:
            try:
                frame.config(bg=self.BG_FRAME, fg=self.FG_COLOR)
            except:
                pass
        for label in self.all_label:
            try:
                label.config(bg=self.BG_FRAME, fg=self.FG_COLOR)
            except:
                pass
        for spin in self.all_spin:
            try:
                spin.config(bg=self.BG_ENTRY, fg=self.FG_COLOR, buttonbackground=self.BG_BUTTON)
            except:
                pass

    def open_reuses_database(self):
        path = askopenfilename(title="Open", filetypes=EXTENSIONS_DB_REUSES)
        if len(path) == 0:
            # No path chosen
            return
        elif path.split(".")[-1] in POSSIBLES_EXTENSIONS:
            # Path chosen in possibles extensions
            self.path_open.set(path)
        else:
            # Path chosen but not supported extension
            showerror("Wrong file format",
                      MESSAGE_ERROR_FORMAT.format(", "
                                                  .join(POSSIBLES_EXTENSIONS)))

    def open_galaxies_database(self):
        # TODO: Delete this method. The format should not be asked with a window but should be set has a param (and defaulting to the value "galaxies.db")
        path = askopenfilename(title="Open", filetypes=EXTENSIONS_GALAXIE)
        self.path_database.set(path)

    def create_reuses_database(self):
        path = env.file_name_galaxies
        # TODO: Check if filepath is valid
        self.path_save.set(path)
        if self.path_open.get() != "":
            create_reuses_database(database_src=self.path_open.get(),
                                   path_file_galaxies=os.path.join(env.path_dir_dest, self.path_save.get()),
                                   path_file_list_galaxies=env.path_file_list_galaxies,
                                   path_file_adjacency_graph=env.path_file_adjacency_graph,
                                   path_file_adjacency_graph_transposed=env.path_file_adjacency_graph_transposed,
                                   path_dir_target=env.path_dir_dest,
                                   max_book_to_add=env.max_book_to_add,
                                   delimiter=env.delimiter,
                                   encoding_src=env.encoding_src,
                                   remove_header=env.remove_header,
                                   index_src_author=env.index_src_author,
                                   index_src_title=env.index_src_title,
                                   index_src_date=env.index_src_date,
                                   index_src_text_matched=env.index_src_text_matched,
                                   index_src_start_byte=env.index_src_start_byte,
                                   index_src_end_byte=env.index_src_end_byte,
                                   index_target_author=env.index_dest_author,
                                   index_target_title=env.index_dest_title,
                                   index_target_date=env.index_dest_date,
                                   index_target_text_matched=env.index_dest_text_matched,
                                   index_target_start_byte=env.index_dest_start_byte,
                                   index_target_end_byte=env.index_dest_end_byte)
        else:
            showerror("No source file",
                      MESSAGE_ERROR_NO_SOURCE_FILE)

    def run(self):
        if self.run_already:
            self.label_res_intro.destroy()
            self.label_res_reuti.destroy()
            self.label_res_auteur.destroy()
            self.label_res_titre.destroy()
            self.label_res_date.destroy()
        if self.path_database.get() != "":
            n = self.spin_n.get()
            p = self.spin_p.get()
            # TODO: Faire ça propre
            intro = "Composante " + n + "\n\n"
            intro += "Réutilisation | Auteur | Titre | Date"
            res_reuti, res_auteur, res_titre, res_date = impressionTexteEtReferenceLongueurGUI(n, p,
                                                                                               self.path_database.get())
            self.label_res_intro = Label(self.run_frame_2, text=intro, justify='left', bg=self.BG_FRAME,
                                         fg=self.FG_COLOR)
            self.label_res_reuti = Label(self.run_frame_2, text=res_reuti, justify='left', bg=self.BG_FRAME,
                                         fg=self.FG_COLOR)
            self.label_res_auteur = Label(self.run_frame_2, text=res_auteur, justify='left', bg=self.BG_FRAME,
                                          fg=self.FG_COLOR)
            self.label_res_titre = Label(self.run_frame_2, text=res_titre, justify='left', bg=self.BG_FRAME,
                                         fg=self.FG_COLOR)
            self.label_res_date = Label(self.run_frame_2, text=res_date, justify='left', bg=self.BG_FRAME,
                                        fg=self.FG_COLOR)

            self.label_res_intro.grid(row=1, pady=10, sticky=W)
            self.label_res_reuti.grid(row=2, column=0, pady=10, sticky=W)
            self.label_res_auteur.grid(row=2, column=1, pady=10, sticky=W)
            self.label_res_titre.grid(row=2, column=2, pady=10, sticky=W)
            self.label_res_date.grid(row=2, column=3, pady=10, sticky=W)

            self.run_already = True

    def _place_menu_bar(self):
        self.menu_bar = Menu(self.window)

        # Create the menu file
        self.menu_file = Menu(self.menu_bar, tearoff=0)
        self.menu_file.add_command(label="Open", accelerator="Ctrl+O", command=self.panel_open_database)
        self.menu_file.add_separator()
        self.menu_file.add_command(label="Create", accelerator="Ctrl+C",
                                   command=lambda x=0, y=False: self.panel_create(x, y))
        self.menu_file.add_command(label="Run", accelerator="Ctrl+R", command=self.panel_run)
        self.menu_file.add_separator()
        self.menu_file.add_command(label="Quit", accelerator="Ctrl+Q", command=self.window.quit)

        # Create the menu parameters
        self.menu_parameters = Menu(self.menu_bar, tearoff=0)
        self.menu_parameters.add_command(label="Edit all", accelerator="Ctrl+P", command=self.panel_edit_parameters)
        self.menu_parameters.add_command(label="Edit step", accelerator="Ctrl+S",
                                         command=lambda x=0, y=1: self.panel_edit_parameters(x, y))
        self.menu_parameters.add_command(label="Edit heading", accelerator="Ctrl+H",
                                         command=lambda x=0, y=0: self.panel_edit_parameters(x, y))

        # Create the menu theme
        self.menu_theme = Menu(self.menu_bar, tearoff=0)
        self.menu_theme.add_command(label="Blue", command=lambda x=BLUE: self.change_theme(x))
        self.menu_theme.add_command(label="Dark", command=lambda x=DARK: self.change_theme(x))
        self.menu_theme.add_command(label="Gray", command=lambda x=GRAY: self.change_theme(x))
        self.menu_theme.add_command(label="Turquoise", command=lambda x=TURQUOISE: self.change_theme(x))

        # Assign all menus to the menu bar
        self.menu_bar.add_cascade(label="Database", menu=self.menu_file)
        self.menu_bar.add_cascade(label="Parameters", menu=self.menu_parameters)
        self.menu_bar.add_cascade(label="Theme", menu=self.menu_theme)
        self.window.config(menu=self.menu_bar)

    def _create_bindings(self):
        self.window.bind_all("<Control-q>", quit)
        self.window.bind_all("<Control-o>", self.panel_open_database)
        self.window.bind_all("<Control-p>", self.panel_edit_parameters)
        self.window.bind_all("<Control-r>", self.panel_run)
        self.window.bind_all("<Control-s>", lambda x=0, y=1: self.panel_edit_parameters(x, y))
        self.window.bind_all("<Control-h>", lambda x=0, y=0: self.panel_edit_parameters(x, y))
        self.window.bind_all("<Control-c>", lambda x=0, y=False: self.panel_create(x, y))

    def quit(self):
        self.window.destroy()


if __name__ == '__main__':
    pass
