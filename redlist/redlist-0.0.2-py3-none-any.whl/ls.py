import sqlite3
from . import category as ctg
from prettytable import PrettyTable

import inquirer

conn = sqlite3.connect("task.db")
cur = conn.cursor()
# table col : id, what, due, importance, category, finished

def list_todo_due():
	""""show todo list by due"""
	slct_data = "select * from todo where finished = ? order by due asc, what asc"
	cur.execute(slct_data,['n'])
	records = cur.fetchall()


	x = PrettyTable()

	x.field_names = ["Finished", "Importance", "What", "due", "category"]


	for row in records:
		x.add_row([row[5], row[3], row[1], row[2], row[4]])
	if not len(records) == 0:
		print(x)
	print("")

def list_todo_importance():
	"""show todo list by importance"""
	slct_data = "select * from todo where finished = ? order by importance asc, what desc"
	cur.execute(slct_data,['n'])
	records = cur.fetchall()

	x = PrettyTable()

	x.field_names = ["Finished", "Importance", "What", "due", "category"]


	for row in records:
		x.add_row([row[5], row[3], row[1], row[2], row[4]])
	if not len(records) == 0:
		print(x)
	print("")

def list_todo_what():
	"""show todo list by what"""
	slct_data = "select * from todo where finished = ? order by what asc"
	cur.execute(slct_data,['n'])
	records = cur.fetchall()

	x = PrettyTable()

	x.field_names = ["Finished", "Importance", "What", "due", "category"]


	for row in records:
		x.add_row([row[5], row[3], row[1], row[2], row[4]])
	if not len(records) == 0:
		print(x)
	print("")

def list_todo_category(category):	# 가나다순
	"""show todo list in category that usr selected"""
	slct_data = "select * from todo where category = ? and finished = ? order by category asc"
	cur.execute(slct_data, [category,'n'])
	records = cur.fetchall()

	x = PrettyTable()

	x.field_names = ["Finished", "Importance", "What", "due", "category"]


	for row in records:
		x.add_row([row[5], row[3], row[1], row[2], row[4]])
	if not len(records) == 0:
		print(x)
	print("")

def list_main():
	opt = [
			inquirer.List('opt',
				message="Choose list option",
				choices=['due', 'what', 'importance', 'category'],
			),
		]
	answers = inquirer.prompt(opt)

	if answers['opt'] == 'due':
		list_todo_due()
	elif answers['opt'] == 'what':
		list_todo_what()
	elif answers['opt'] == 'importance':
		list_todo_importance()
	elif answers['opt'] == 'category':
		ctg.show_category()
		c = str(input("What cateogry do you want to list? "))
		cmp_data = "select distinct category from todo"
		cur.execute(cmp_data)
		cmp_records = cur.fetchall()
		cmp_list = []
		for i in range(len(cmp_records)):
			cmp_list.append(cmp_records[i][0])
		while True:
			if not c in cmp_list:
				print("There is not", c, "Please enter the 'what' in table")
				c = str(input())
			else:
				break
		list_todo_category(c)
