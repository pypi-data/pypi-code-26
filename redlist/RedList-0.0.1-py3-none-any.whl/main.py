import sqlite3
from . import logo as lg
from . import add_todo as at
from . import ls as li
from . import create_table as ct
from . import modify as md
from . import del_todo as dl
from . import category as ctg
from . import auto_finish as af

import inquirer

def main():
	lg.print_logo()
	ct.create_table()
	run_program()

def run_program():
	while True:
		print("Choose what to do")
		af.auto_fin()
		mode = [
			inquirer.List('mode',
				message="Choose what to do",
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
		
# if __name__ == "__main__":
# 	lg.print_logo()
# 	ct.create_table()
# 	run_program()
