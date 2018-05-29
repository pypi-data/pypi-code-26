def bcolors(fg="white", bg="black", styles=[]):
    colors_fg = {
        "black": 30,
        "red": 31,
        "green": 32,
        "orange": 33,
        "blue": 34,
        "purple": 35,
        "cyan": 36,
        "white": 37
    }
    
    colors_bg = {
        "black": 40,
        "red": 41,
        "green": 42,
        "orange": 43,
        "blue": 44,
        "purple": 45,
        "cyan": 46,
        "white": 47
    }
    
    all_styles = {
        "none": 0,
        "bold": 1,
        "shadow": 2,
        "italic": 3,
        "underlined": 4,
        "flashing": 5,
        "removed": 9
    }
    try:
        out = "\033[%d;%d%sm" % (colors_fg[fg], colors_bg[bg], "".join(map(lambda x: ";%s" % str(all_styles[x]), styles)))
    except KeyError:
        raise ValueError("Seems like you have passed invalid colors or styles.")
    return out


def get_colored(color, text):
    return color+text+bcolors(styles=["none"])


def get_warning(text):
    return get_colored(bcolors(fg="orange", styles=["flashing"]), text)


def get_wrong(text):
    return get_colored(bcolors(fg="orange"), text)


def get_red(text):
    return get_colored(bcolors(fg="red"), text)


def get_danger(text):
    return get_colored(bcolors(fg="red", styles=["flashing"]), text)


def get_success(text):
    return get_colored(bcolors(fg="green"), text)
   
    
def print_colored(color, text):
    print(color+text+bcolors(styles=["none"]))


def print_warning(text):
    print(get_warning(text))


def print_wrong(text):
    print(get_wrong(text))


def print_danger(text):
    print(get_danger(text))


def print_success(text):
    print(get_success(text))
