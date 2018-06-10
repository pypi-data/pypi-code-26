from tkinter import *
import os

from galaxies.src.gui.galaxie_creation import WindowsGalaxieCreation
from galaxies.src.gui.galaxie_vizualisation import WindowsGalaxieVizualisation


PATH_FILE_LOGO_SORBONNE = os.path.join(os.path.dirname(__file__),
                                       "../../res/logo_sorbonne.gif")
PATH_FILE_LOGO_LIP6 = os.path.join(os.path.dirname(__file__),
                                   "../../res/logo_lip6.gif")


class WindowMainMenu:
    def __init__(self):
        self.window = Tk()
        self.window.geometry("800x400")
        self.window.overrideredirect(True)

        self.quit_button = Button(self.window, text="X",
                                  command=self.window.quit, relief=FLAT,
                                  foreground='red',
                                  font=("Helvetica", 10, "bold"))
        self.quit_button.grid(row=0, columnspan=2, sticky=NE, padx=5)

        self.title = Label(text="GALAXIES",
                           font=("Helvetica", 25, "bold italic"),
                           fg='#%02x%02x%02x' % (29, 40, 105))
        self.title.grid(row=1, columnspan=2, pady=15)

        self.create_button = Button(self.window, text="Create a galaxies' graph",
                                    width=30, height=5,
                                    fg='#%02x%02x%02x' % (29, 40, 105),
                                    command=self.open_create)
        self.explore_button = Button(self.window, text="Explore a galaxies' graph",
                                     width=30, height=5,
                                     fg='#%02x%02x%02x' % (29, 40, 105),
                                     command=self.open_explore)

        self.create_button.grid(row=2, column=0)
        self.explore_button.grid(row=2, column=1)

        self.canvas = Canvas(self.window, width=800, height=200)

        self.logo_sorbonne = PhotoImage(file=PATH_FILE_LOGO_SORBONNE)
        self.logo_lip6 = PhotoImage(file=PATH_FILE_LOGO_LIP6)

        self.canvas.create_image(200, 120, image=self.logo_sorbonne)
        self.canvas.create_image(600, 110, image=self.logo_lip6)

        self.canvas.grid(row=3, columnspan=2)
        self.center(self.window)
        self.window.mainloop()

    def center(self, toplevel):
        """ Center the window at the middle of the screen.
        Source :
        https://stackoverflow.com/a/3353112
        """
        # TODO: Issue with multi-monitors

        toplevel.update_idletasks()
        w = toplevel.winfo_screenwidth()
        h = toplevel.winfo_screenheight()
        size = tuple(
            int(_) for _ in toplevel.geometry().split('+')[0].split('x'))
        x = w / 2 - size[0] / 2
        y = h / 2 - size[1] / 2
        toplevel.geometry("%dx%d+%d+%d" % (size + (x, y)))

    def open_create(self):
        self.quit()
        WindowsGalaxieCreation()

    def open_explore(self):
        self.quit()
        WindowsGalaxieVizualisation()

    def quit(self):
        self.window.destroy()


if __name__ == "__main__":
    pass
