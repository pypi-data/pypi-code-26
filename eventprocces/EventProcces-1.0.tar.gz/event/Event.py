import MySQLdb
from EventLib.event import Event
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


conn = MySQLdb.connect(host='localhost', port=3306,
                       user='root', passwd='giwera', db='calendar')
cur = conn.cursor()
tomorrow = datetime.now().date() + timedelta(days=1)


def addEvent(arg):

    if (arg.periodType == "day"):
        insert(arg, "days")
    if (arg.periodType == "week"):
        insert(arg, "weeks")
    if (arg.periodType == "month"):
        insert(arg, "months")
    if (arg.periodType == "year"):
        insert(arg, "years")
    conn.commit()


def getAll(arg):
    if arg == 1:
        selectAll = ("SELECT * FROM event "
                     "WHERE isFinished = 0 ORDER BY startDate ASC")
    if arg == 2:
        selectAll = ("SELECT * FROM event "
                     "WHERE isFinished = 1 ORDER BY startDate DESC")
    cur.execute(selectAll)
    conn.commit()
    events = []
    for row in cur:
        event = Event()
        event.id = row[0]
        event.name = row[1]
        event.description = row[2]
        event.startDate = row[3]
        event.periodType = row[4]
        event.periodFrequency = row[5]
        event.isFinished = row[6]
        events.append(event)
    return events


def delete(id):
    deleteQuery = ("DELETE FROM event WHERE event.id = %s") % (id)
    cur.execute(deleteQuery)
    conn.commit()


def insert(arg, period):
    add_event = ("INSERT INTO event "
                 "(name, description, startDate,"
                 " periodType, periodFrequency, isFinished) "
                 "VALUES (%s, %s, %s, %s, %s, %s)")

    data = (arg.name, arg.description, arg.startDate, arg.periodType,
            arg.periodFrequency, arg.isFinished)
    cur.execute(add_event, data)

    counter = int(arg.periodFrequency)
    if period == "days":
        while counter != 0:
            data = (arg.name, arg.description,
                    arg.startDate + relativedelta(days=+counter),
                    arg.periodType, arg.periodFrequency, arg.isFinished)
            cur.execute(add_event, data)
            counter = counter - 1

    if period == "weeks":
        while counter != 0:
            data = (arg.name, arg.description,
                    arg.startDate + relativedelta(weeks=+counter),
                    arg.periodType, arg.periodFrequency, arg.isFinished)
            cur.execute(add_event, data)
            counter = counter - 1

    if period == "months":
        while counter != 0:
            data = (arg.name, arg.description,
                    arg.startDate + relativedelta(months=+counter),
                    arg.periodType, arg.periodFrequency, arg.isFinished)
            cur.execute(add_event, data)
            counter = counter - 1

    if period == "years":
        while counter != 0:
            data = (arg.name, arg.description,
                    arg.startDate + relativedelta(years=+counter),
                    arg.periodType, arg.periodFrequency, arg.isFinished)
            cur.execute(add_event, data)
            counter = counter - 1


def update(arg):
    update_event = ("UPDATE event SET name = %s, description = %s,"
                    " startDate = %s, isFinished = %s"
                    " WHERE id = %s")
    data = (arg.name, arg.description, arg.startDate, arg.isFinished, arg.id)
    cur.execute(update_event, data)
    conn.commit()
