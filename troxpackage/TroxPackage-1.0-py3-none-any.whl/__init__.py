import sqlite3
name = "TroxPackage"

def showParkings():
    conn = sqlite3.connect("ParkingDB.sqlite")
    c = conn.cursor()
    c.execute('SELECT * FROM Parking')
    for row in c:
        print(row)
    conn.close()

def addParking(cap, ava, restrictions):
    conn = sqlite3.connect("ParkingDB.sqlite")
    c = conn.cursor()
    newParking = (cap, ava, restrictions)
    with conn:
        c.execute('''INSERT INTO Parking(capacity, availability, restrictions) VALUES(?,?,?)''', newParking)
    conn.close()

def isUserOnParking(userID):
    conn = sqlite3.connect("ParkingDB.sqlite")
    c = conn.cursor()
    with conn:
        c.execute('''SELECT ParkingID FROM User WHERE iD = ?''', str(userID))
    id = c.fetchone()[0]
    if id == -1:
        print("User outside of parking")
    else:
        print("User on parking number :", id)

    conn.close()




