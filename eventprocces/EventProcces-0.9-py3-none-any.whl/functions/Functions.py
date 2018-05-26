from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from EventLib.event import Event
from tkinter import messagebox
import time


def printAll(events):
    counter = 1
    for event in events:
        print("%s.  Nazwa: %s \n"
              "    Opis: %s \n"
              "    Data: %s \n"
              % (counter, event.name, event.description, event.startDate))
        counter = counter + 1


def check():
    while 1:
        events = Event.getAll(1)
        for event in events:
            if event.startDate <= datetime.combine(date.today(),
                                                   datetime.today().time()):
                event.isFinished = 1
                Event.update(event)

        events = Event.getAll(1)
        for event in events:
            if event.startDate + relativedelta(days=-2) \
                    <= datetime.combine(date.today(), datetime.today().time()):
                messagebox.showinfo("Przypomnienie",
                                    "W przeciągu 2 dni"
                                    " masz następujące wydarzenie: \n"
                                    " Nazwa: %s \n"
                                    " Opis: %s \n"
                                    " Data: %s \n"
                                    % (event.name, event.description,
                                       event.startDate))
        time.sleep(10)
