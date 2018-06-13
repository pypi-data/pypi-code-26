# -*- coding: utf-8 -*-
from colorama import Fore
import main

def print_logo():
	"""
	   ___         __  __   _     __
	  / _ \___ ___/ / / /  (_)__ / /_
	 / , _/ -_) _  / / /__/ (_-</ __/
	/_/|_|\__/\_,_/ /____/_/___/\__/
	by Team Avengers
	MIT LICENSE
	VERSION 0.1.0
	"""

	print(Fore.RED + "   ___         __  __   _     __ \n  / _ \___ ___/ / / /  (_)__ / /_\n / , _/ -_) _  / / /__/ (_-</ __/\n/_/|_|\__/\_,_/ /____/_/___/\__/ \n")
	print("by Team Avengers\nMIT LICENSE\nVERSION {}\n\n".format(main.version()) + Fore.RESET)