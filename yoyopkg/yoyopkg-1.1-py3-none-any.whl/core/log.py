from colorama import init
init()

from colorama import Fore, Style

def pdebug(src):
    print(Fore.WHITE + str(src) + Style.RESET_ALL)

def pinfo(src):
    print(Fore.LIGHTBLUE_EX + str(src) + Style.RESET_ALL)

def pwarning(src):
    print(Fore.YELLOW + str(src) + Style.RESET_ALL)

def perror(src):
    print(Fore.LIGHTRED_EX + str(src) + Style.RESET_ALL)

def psuccess(src):
    print(Fore.GREEN + str(src) + Style.RESET_ALL)