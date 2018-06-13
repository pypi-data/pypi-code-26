# -*- coding: utf-8 -*-
import sqlite3
try:
	from . import logo as lg
	from . import add_todo as at
	from . import ls as li
	from . import create_table as ct
	from . import modify as md
	from . import del_todo as dl
	from . import category as ctg
	from . import auto_finish as af
	from . import duecheck as dc
except:
	import logo as lg
	import add_todo as at
	import ls as li
	import create_table as ct
	import modify as md
	import del_todo as dl
	import category as ctg
	import auto_finish as af
	import duecheck as dc

import inquirer
from optparse import OptionParser
import sys
from pathlib import Path


home_dir = str(Path.home())
conn = sqlite3.connect(home_dir + "/task.db")
cur = conn.cursor()


def main():
	ct.create_table()
	cmd_line()

def chk_is_there(x):
	cmp_data = "select distinct what from todo"
	cur.execute(cmp_data)
	cmp_records = cur.fetchall()
	cmp_list = []
	for i in range(len(cmp_records)):
		cmp_list.append(cmp_records[i][0])
	if not x in cmp_list:
		print("There is not", x)
		exit()


def cmd_line():
	"""Usr inputs option among -a(add todo), -l(list todo), -m(modify todo), -d(delete todo), -c(show category)"""

	usage = "Usage: %prog [options]"
	parser = OptionParser(usage=usage, version="%prog {}".format(version()))
	parser.add_option("-a", dest="add", action='store', type=str, default=False, help="add a new todo",
						metavar="[what] [due(yyyy-mm-dd hh:mm:ss)] [importance(0~5)] [category]")
	parser.add_option("-l", dest="list", action='store', type=str, default=False, help="list todos by option",
						metavar="what || due || importance || category [category]")
	parser.add_option("-m", dest="modify", action='store', type=str, default=False, help="modify the todo",
						metavar="[org_what] [what] [due(yyyy-mm-dd hh:mm:ss)] [importance(0~5)] [category] [finished(y/n)]")
	parser.add_option("-d", dest="delete", action='store', type=str, default=False, help="delete the todo",
						metavar="[what]")
	parser.add_option("-c", dest="category", action='store_true', default=False, help="show categories")

	options, args = parser.parse_args()

	# no option
	if len(args) == 0 and not (options.add or options.list or options.modify or options.delete or options.category):
		lg.print_logo()
		run_program()

	if options.add:
		sql = "insert into todo (what, due, importance, category, finished) values (?, ?, ?, ?, ?)"
		what, due, importance, category = options.add, args[0]+" "+args[1], args[2], args[3]
		if not dc.isdue(due):
			print('Invaild input! Please check your input(yyyy-mm-dd hh:mm:ss)')
			exit()
		data = [what, due, importance, category, "n"]
		cur.execute(sql, data)
		print("ADDED")
		conn.commit()

	if options.list:
		op = options.list
		if op == 'what':
			li.list_todo_what()
		elif op == 'due':
			li.list_todo_due()
		elif op == 'importance':
			li.list_todo_importance()
		elif op == 'category':
			# check whether category is exsited in todo table
			c = args[0]
			cmp_data = "select distinct category from todo"
			cur.execute(cmp_data)
			cmp_records = cur.fetchall()
			cmp_list = []
			for i in range(len(cmp_records)):
				cmp_list.append(cmp_records[i][0])
			if not c in cmp_list:
				print("There is not", c)
			li.list_todo_category(c)

	if options.modify:
		modify_data = options.modify
		# check whether there is the modify val in table
		chk_is_there(modify_data)

		what, due, importance, category, finished = args[0], args[1]+" "+args[2], args[3], args[4], args[5]
		sql = "update todo set what = ?, due = ?, importance = ?, category = ?, finished = ? where what = ?"
		cur.execute(sql, [what, due, int(importance), category, finished, modify_data])
		print("MODIFIED")
		conn.commit()

	if options.delete:
		delete_data = options.delete
		# check whether there is the delete_data val in table
		chk_is_there(delete_data)

		del_record = "delete from todo where what = ?"
		cur.execute(del_record, [delete_data])
		print("DELETED")
		conn.commit()

	if options.category:
		ctg.show_category()



def run_program():
	"""Run program if usr executes RedList without any option"""
	while True:
		af.auto_fin()
		mode = [
			inquirer.List('mode',
				message="Choose what you ganna do",
				choices=['Add todo', 'List todo', 'Modify todo', 'Delete todo', 'Show category', 'Quit'],
			),
		]
		answers = inquirer.prompt(mode)
		if answers['mode'] == 'Add todo':
			at.add_todo()
		elif answers['mode'] == 'List todo':
			li.list_main()
		elif answers['mode'] == 'Modify todo':
			md.modify_todo()
		elif answers['mode'] == 'Delete todo':
			dl.del_todo()
		elif answers['mode'] == 'Show category':
			ctg.show_category()
		elif answers['mode'] == 'Quit':
			break
		af.auto_fin()

if __name__=="__main__":
	main()
