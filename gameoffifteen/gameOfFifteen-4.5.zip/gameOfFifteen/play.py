import tkinter as tk
from guimain import GuiMain


def play():
	root = tk.Tk()
	gui = GuiMain(root)
	root.mainloop()
	
if __name__ == "__main__":
    play()
	