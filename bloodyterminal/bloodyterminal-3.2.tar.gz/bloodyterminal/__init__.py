from colorama import Fore, Style, init
import colorama

colorama.init(strip=False)
init()


class btext:

    def __init__(self):
        print(Style.RESET_ALL)

    def success(str):
        print(Fore.GREEN + '[SUCCESS] ' + str + Style.RESET_ALL)

    def info(str):
        print(Fore.YELLOW + '[INFO] ' + str + Style.RESET_ALL)

    def warning(str):
        print(Fore.RED + '[WARNING] ' + str + Style.RESET_ALL)

    def error(str):
        print(Fore.LIGHTRED_EX + '[ERROR] ' + str + Style.RESET_ALL)

    def debug(str):
        print(Fore.MAGENTA + '[DEBUG] ' + str + Style.RESET_ALL)

    def custom(str1, str2):
        print(Fore.CYAN + '[%s] ' % str1 + str2 + Style.RESET_ALL)

    def demo():
        btext.success("your string")
        btext.info("your string")
        btext.warning("your string")
        btext.error("your string")
        btext.debug("your string")
        btext.custom("your prefix", "your string")
