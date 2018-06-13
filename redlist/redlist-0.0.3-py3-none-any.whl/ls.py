import sqlite3
try:
	from . import category as ctg
except:
	import category as ctg
from prettytable import PrettyTable

from colorama import Fore
import inquirer
from pathlib import Path


home_dir = str(Path.home())
conn = sqlite3.connect(home_dir + "/task.db")
cur = conn.cursor()
# table col : id, what, due, importance, category, finished

def list_todo_due():
	""""show todo list by due"""
	slct_data = "select * from todo where finished = ? order by due asc, what asc"
	cur.execute(slct_data,['n'])
	records = cur.fetchall()
	print(Fore.RED + "\nORDER BY DUE" + Fore.RESET)
	print_list(records)


def list_todo_importance():
	"""show todo list by importance"""
	slct_data = "select * from todo where finished = ? order by importance desc, what asc"
	cur.execute(slct_data,['n'])
	records = cur.fetchall()
	print(Fore.RED + "\nORDER BY IMPORTANCE" + Fore.RESET)
	print_list(records)


def list_todo_what():
	"""show todo list by what"""
	slct_data = "select * from todo where finished = ? order by what asc"
	cur.execute(slct_data,['n'])
	records = cur.fetchall()
	print(Fore.RED + "\nORDER BY WHAT" + Fore.RESET)
	print_list(records)


def list_todo_category(category):	# 가나다순
	"""show todo list in category that usr selected"""
	slct_data = "select * from todo where category = ? and finished = ? order by category asc"
	cur.execute(slct_data, [category,'n'])
	records = cur.fetchall()
	print(Fore.RED + "\nORDER BY WHAT IN "+category + Fore.RESET)
	print_list(records)


def print_list(records):
	x = PrettyTable()

	x.field_names = ["Finished", "Importance", "What", "due", "category"]

	check = u"\u2713"
	uncheck = u"\u2718"

	for row in records:
		if row[5] == 'n':
			x.add_row([uncheck, row[3], row[1], row[2], row[4]])
		elif row[5] == 'y':
			x.add_row([check, row[3], row[1], row[2], row[4]])
	if not len(records) == 0:
		print(x)
	print("")

def chk_is_there(x):
	cmp_data = "select distinct category from todo"
	cur.execute(cmp_data)
	cmp_records = cur.fetchall()
	cmp_list = []
	for i in range(len(cmp_records)):
		cmp_list.append(cmp_records[i][0])
	while True:
		if not x in cmp_list:
			print("There is not", x)
			c = str(input("What cateogry do you want to list? "))
		else:
			break
			

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
		chk_is_there(c)
		
		list_todo_category(c)
