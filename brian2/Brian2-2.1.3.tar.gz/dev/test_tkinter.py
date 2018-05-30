import Tkinter as tk
#from Tkinter import ttk

class Application(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.style = tk.Style()
        self.style.configure('.', font=('sans', 12))
        self.pack()
        self.createWidgets()

    def createWidgets(self):
        self.hi_there = ttk.Button(self)
        self.hi_there["text"] = "Hello World\n(click me)"
        self.hi_there["command"] = self.say_hi
        self.hi_there.pack(side="top")

        self.QUIT = ttk.Button(self, text="QUIT",
                               command=root.destroy)
        self.QUIT.pack(side="bottom")
    def say_hi(self):
        print("hi there, everyone!")

root = tk.Tk()
app = Application(master=root)
app.mainloop()

