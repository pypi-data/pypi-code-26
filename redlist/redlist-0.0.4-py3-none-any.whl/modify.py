# -*- coding: utf-8 -*-
import sqlite3
from pathlib import Path

try:
	from . import duecheck as dc
	from . import ls as li
except:
	import duecheck as dc
	import ls as li

def modify_todo():
	home_dir = str(Path.home())
	conn = sqlite3.connect(home_dir + "/task.db")
	cur = conn.cursor()

	slct_data = "select * from todo where 1 order by finished asc, what asc"
	cur.execute(slct_data)
	records = cur.fetchall()
	li.print_list(records)

	modify = str(input("What todo do you want to modify? Please enter 'what' "))

	# check whether there is the modify val in table
	cmp_data = "select distinct what from todo"
	cur.execute(cmp_data)
	cmp_records = cur.fetchall()
	cmp_list = []
	for i in range(len(cmp_records)):
		cmp_list.append(cmp_records[i][0])
	while True:
		if not modify in cmp_list:
			print("There is not", modify, "Please enter the 'what' in table")
			modify = str(input())
		else:
			break

	org_data = "select * from todo where what = ?"
	cur.execute(org_data, [modify])
	org_record = cur.fetchall()
	# table col : id, what, due, importance, category, finished
	
	what_m = str(input("What? "))
	if what_m == '':
		what_m = org_record[0][1]

	while True:
		due_m = str(input("Due? (yyyy-mm-dd hh:mm:ss) "))
		if dc.isdue(due_m):
			break
		elif due_m == '':
			due_m = org_record[0][2]
			break
		else:
			print('Invaild input! Please check your input')

	while True:
		importance_m = str(input("Importance? (1 ~ 5) "))
		if importance_m == '':
			importance_m = org_record[0][3]
			break
		elif importance_m.isdigit() and 1 <= int(importance_m) <= 5:
			break
		else:
			print('Invaild input! Please check your input')

	category_m = str(input("Category? "))

	if category_m == '':
		category_m = org_record[0][4]

	while True:
		finished_m = input("Finished (y: yes, n: no)? ")
		if finished_m == '':
			finished_m = org_record[0][5]
			break
		elif finished_m == 'y' or finished_m == 'n':
			break
		else:
			print('Invaild input! Please check your input')

	sql = "update todo set what = ?, due = ?, importance = ?, category = ?, finished = ? where what = ?"

	cur.execute(sql, [what_m, due_m, int(importance_m), category_m, finished_m, modify])
	conn.commit()
	print("")
