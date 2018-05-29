import os
import random

from try_pkg import colors

DATA_DIR = os.path.join(os.getenv("HOME"), ".app.py")   # Here set your DATA path if you have your data stored somewhere else than in default location
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)
    print("Created new data directory: '%s'" % DATA_DIR)


class Data:
    def __init__(self, file_name):
        self.file_name = file_name
        self.data_one = {}
        self.data_two = {}
    
    def load(self):
        with open(self.file_name) as file:
            for line in file:
                if not line:
                    break
                else:
                    line = line[:-1]
                one, two = line.split("\t")
                self.data_one[one] = two
                self.data_two[two] = one
    
    def exists(self):
        return os.path.exists(self.file_name)
        
    def translate_one(self, word):
        if word not in self.data_one:
            raise ValueError
        return self.data_one[word]

    def translate_two(self, word):
        if word not in self.data_two:
            raise ValueError
        return self.data_two[word]
    
    def add(self, word_one, word_two):
        self.data_one[word_one] = word_two
        self.data_two[word_two] = word_one
    
    def remove(self, word):
        del self.data_two[self.translate_one(word)]
        del self.data_one[word]
    
    def list(self):
        return sorted(self.data_one, key=lambda s: (s if s[:3] not in ["das", "die", "der"] else s[4:]).lower())
    
    def save(self):
        with open(self.file_name, "w") as file:
            for one in self.list():
                file.write("%s\t%s\n" % (one, self.data_one[one]))
        
    def get_random(self):
        return random.choice(list(self.data_one.keys()))
    
    def ask_one(self, word):
        print(">> %s" % word)
        two = input("\t")
        if not two:
            print("Correct answer is '%s'." % self.translate_one(word))
            self.ask_one(word)
        elif two == self.translate_one(word):
            colors.print_success("Correct.")
        else:
            colors.print_wrong("Wrong. You entered '%s' instead of '%s'." % (two, self.translate_one(word)))
            self.ask_one(word)
    
    def ask_two(self, word):
        print(">> %s" % word)
        one = input("\t")
        if not one:
            print("Correct answer is '%s'." % self.translate_two(word))
            self.ask_two(word)
        elif one == self.translate_two(word):
            colors.print_success("Correct.")
        else:
            print(colors.get_wrong("Wrong. You entered '") + self.get_coloured(one, self.translate_two(word)) + colors.get_wrong("' instead of '%s'." % self.translate_two(word)))
            self.ask_two(word)
    
    def get_coloured(self, one, orig):
        out = ""
        for i in range(min(len(one), len(orig))):
            if one[i] != orig[i]:
                return colors.get_success(out) + colors.get_red(one[i:])
            out += one[i]
        else:
            if len(one) < len(orig):
                return colors.get_success(one) + colors.get_red("_" * (len(orig) - len(one)))
            elif len(one) > len(orig):
                return colors.get_success(one[:len(orig)]) + colors.get_red(one[len(orig):])
            return colors.get_success(out)
