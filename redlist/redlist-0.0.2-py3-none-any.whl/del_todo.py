# -*- coding: utf-8 -*-
import sqlite3
from . import create_table as ct

def del_todo():
	conn = sqlite3.connect("task.db")
	cur = conn.cursor()

	slct_data = "select * from todo where finished = 0 order by what asc"
	# finished = 0 일때를 보여줄지, finished 값과 상관없이 보여줄지 고민
	cur.execute(slct_data)
	records = cur.fetchall()
	for row in records:
		print(row[5], row[3], row[1], row[2], row[4])

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
