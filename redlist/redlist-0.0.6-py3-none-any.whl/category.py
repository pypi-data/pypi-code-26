import sqlite3
from prettytable import PrettyTable
from pathlib import Path

def show_category():
	home_dir = str(Path.home())
	conn = sqlite3.connect(home_dir + "/task.db")
	cur = conn.cursor()

	slct_data = "select distinct category from todo where 1 order by category asc"
	cur.execute(slct_data)
	records = cur.fetchall()

	x = PrettyTable()

	x.field_names = ["category"]

	for row in records:
		x.add_row([row[0]])
	if not len(records) == 0:
		print(x)
	print("")
