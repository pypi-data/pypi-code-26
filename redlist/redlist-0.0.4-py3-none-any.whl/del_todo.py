# -*- coding: utf-8 -*-
import sqlite3
try:
	from . import create_table as ct
	from . import ls as li
except:
	import create_table as ct
	import ls as li
from pathlib import Path

def del_todo():
	home_dir = str(Path.home())
	conn = sqlite3.connect(home_dir + "/task.db")
	cur = conn.cursor()

	slct_data = "select * from todo where finished = 'n' order by what asc"
	# finished = 0 일때를 보여줄지, finished 값과 상관없이 보여줄지 고민
	cur.execute(slct_data)
	records = cur.fetchall()

	li.print_list(records)

	delete_data = str(input("What todo do you delete? Please enter the 'what' "))

	# check whether there is the delete_data val in table
	cmp_data = "select distinct what from todo"
	cur.execute(cmp_data)
	cmp_records = cur.fetchall()
	cmp_list = []
	for i in range(len(cmp_records)):
		cmp_list.append(cmp_records[i][0])
	while True:
		if not delete_data in cmp_list:
			print("There is not", delete_data, "Please enter the 'what' in table")
			delete_data = str(input())
		else:
			break

	del_record = "delete from todo where what = ?"
	cur.execute(del_record, [delete_data])
	conn.commit()

	print("")
