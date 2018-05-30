"""
licenseit

Usage:
	licenseit new
	licenseit init
	licenseit -h | --help
	licenseit -v | --version

Options:
    
    	new 		Creates a LICENSE file.
    	init    	Creates a LICENSE file.
	-h --help	Shows possible commands.
	-v --version	Shows current version of the package.

Help:
	For suggestions/problems and etc. visit the github reposityory https://github.com/monzita/licenseit
"""
import datetime as dt
import re

from docopt import docopt

from licenseit.commands.new import New

VERSION = '0.0.2'

def main():
	global VERSION
	options = docopt(__doc__, version=VERSION)

	licenses = [
		"""Choose a license:
		1. Adaptive public license
		2. Apache license-2.0
		3. Artistic License 2.0
		4. BSD-2-Clause-Patent
		5. BSD-2-Clause
		6. BSD-3-Clause
		7. Common Development and Distribution License
		8. Educational Community License
		9. Eclipse Public License - v 2.0
		10. GNU GENERAL PUBLIC LICENSE 2.0
		11. GNU GENERAL PUBLIC LICENSE 3.0
		12. IPA Font License Agreement v1.0
		13. ISC
		14. GNU LIBRARY GENERAL PUBLIC LICENSE 2.0
		15. GNU LIBRARY GENERAL PUBLIC LICENSE 3.0
		16. MIT
		17. Mozilla Public License, version 2.0
		18. NASA OPEN SOURCE AGREEMENT VERSION 1.3
		19. SIL OPEN FONT LICENSE
		20. OSET PUBLIC LICENSE 2.1
		21. Upstream Compatibility License v. 1.0 (UCL-1.0)""",
	]

	if options['new'] or options['init']:
		choices = {}

		print(licenses[0])
		user_choice = input("License (default MIT): ")

		if user_choice:
			if re.findall(r"[^\d]+", user_choice):
				while re.findall(r"[^\d]+", user_choice):
					user_choice = input("Enter a valid number of a license: ")
			else:
				while int(user_choice) < 0 or int(user_choice) > 21:
					user_choice = input("Enter a valid number of a license: ")
		else:
			user_choice = 16

		choices['license'] = int(user_choice)
		choices['author'] = input("Author | Organization: ")
		current_year = dt.datetime.now().year
		choices['year'] = input("Year (default " + str(current_year) + "): ").strip()

		if re.findall(r"[^\d+]+", choices['year']):
				while re.findall(r"[^\d+]+", choices['year']):
					choices['year'] = input("Enter a valid year: ")
		else:
			choices['year'] = int(choices['year'] or current_year)
	
		command = New(choices)
		command.exec()
	elif options['-v']:
		print(VERSION)