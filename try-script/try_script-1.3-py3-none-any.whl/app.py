#! /bin/env python3
import os
import random

from getdata import DATA_DIR, Data
from colors import *


def main():
    print("Welcome to this awesome vocabulary learning app.")
    try:
        while True:
            try:
                print("Do you want to (t)rain, (l)ist, (m)odify, (a)dd or (r)emove word sets, (A)dd or (R)emove language or (e)xit")
                action = ""
                while not action:
                    action = input(">> ").split()[0]
                if action not in "tlmarRAe":
                    print_wrong("Invalid option.")
                    continue
                elif action in "tlmar":

                    print("Choose your desired language:")
                    languages = [lang for lang in os.listdir(DATA_DIR)]

                    for i, lang in enumerate(languages):
                        print("%d %s" % (i+1, lang))

                    lang = int(input("Enter number 1-%d >> " % len(languages)))
                    print("You chose %s." % languages[lang-1])
                    current_dir = os.path.join(DATA_DIR, languages[lang-1])
                    if action == "a":
                        group = input("What is the name for your new group?")
                        print_warning("WARNING")
                        if input("Are you sure you want to add new group '%s'? (y/n) " % group).lower()!="y":
                            print_wrong("Aborting ...")
                            continue
                        file = os.path.join(current_dir, group)
                        data = Data(file)
                        if data.exists():
                            print_wrong("This group already exists. Aborting ...")
                        else:
                            data.save()
                            print_success("Successfully created new group.")
                    elif action == "r":
                        print("Choose group you want to delete:")
                        groups = [group for group in os.listdir(current_dir)]

                        for i, group in enumerate(groups):
                            print("%d %s" % (i+1, group))

                        group = int(input("Enter number 1-%d >> " % len(groups)))
                        print_danger("DANGEROUS")
                        if input("Are you sure you want to delete this group '%s'? This action CANNOT be undone. (y/n) " % groups[group-1]).lower()!="y":
                            continue
                        os.remove(os.path.join(current_dir, groups[group-1]))
                        print_success("Done.")
                    elif action == "l":
                        print("Choose group you want to list:")
                        groups = [group for group in os.listdir(current_dir)]

                        for i, group in enumerate(groups):
                            print("%d %s" % (i+1, group))

                        group = int(input("Enter number 1-%d >> " % len(groups)))
                        data = Data(os.path.join(current_dir, groups[group-1]))
                        data.load()
                        for one in data.list():
                            print(">> %s" % one)
                            print("\t>> %s" % data.data_one[one])
                    elif action == "m":
                        print("Choose group you want to modify:")
                        groups = [group for group in os.listdir(current_dir)]

                        for i, group in enumerate(groups):
                            print("%d %s" % (i+1, group))

                        group = int(input("Enter number 1-%d >> " % len(groups)))
                        data = Data(os.path.join(current_dir, groups[group-1]))
                        data.load()
                        try:
                            while True:
                                print("Do you want to (r)emove words, (a)dd them, (s)ave or (e)xit?")
                                action = input(">> ").split()[0]
                                if action not in "arse":
                                    print_wrong("Invalid option.")
                                    continue
                                elif action == "a":
                                    while True:
                                        one = input("1 >> ")
                                        if not one:
                                            break
                                        two = input("\t\t2 >> ")
                                        data.add(one, two)
                                    print_success("Hopefully everything was added.")
                                elif action == "r":
                                    one = input("Insert translation in first language: ")
                                    try:
                                        data.remove(one)
                                        print_success("Removed.")
                                    except ValueError:
                                        print_wrong("This word doesn't exists.")
                                elif action == "s":
                                    data.save()
                                    print_success("Saved.")
                                elif action == "e":
                                    data.save()
                                    break

                        except KeyboardInterrupt:
                            print()
                            print("Try command 'e' next time ;)")
                            print("This method won't save your modifications.")
                    elif action == "t":
                        print("Choose group you want to train on:")
                        groups = [group for group in os.listdir(current_dir)]

                        for i, group in enumerate(groups):
                            print("%d %s" % (i+1, group))

                        group = int(input("Enter number 1-%d >> " % len(groups)))
                        data = Data(os.path.join(current_dir, groups[group-1]))
                        data.load()
                        if input("Do you want random infinite selection? (y/n)").lower() == "y":
                            try:
                                while True:
                                    if random.random() > 0.8:
                                        data.ask_one(data.get_random())
                                    else:
                                        data.ask_two(data.translate_one(data.get_random()))
                            except KeyboardInterrupt:
                                print()
                        else:
                            try:
                                for word in data.list():
                                    data.ask_two(data.translate_one(word))
                            except KeyboardInterrupt:
                                print()
                elif action == "R":
                    print("Choose language you want to delete:")
                    languages = [lang for lang in os.listdir(DATA_DIR)]

                    for i, lang in enumerate(languages):
                        print("%d %s" % (i+1, lang))

                    lang = int(input("Enter number 1-%d >> " % len(languages)))
                    print_danger("DANGEROUS")
                    if input("Are you sure you want to delete this language '%s'? This action CANNOT be undone. (y/n) " % languages[lang-1]).lower()!="y":
                        print_wrong("Aborting ...")
                        continue
                    from shutil import rmtree
                    rmtree(os.path.join(DATA_DIR, languages[lang-1]))
                    print("Deleted successfully.")
                elif action == "A":
                    lang = input("What is your new language?\n>> ")
                    print_warning("WARNING")
                    if input("Are you sure you want to add language '%s'? (y/n) " % lang).lower()!="y":
                        print_wrong("Aborting ...")
                        continue
                    folder = os.path.join(DATA_DIR, lang)
                    if not os.path.exists(folder):
                        os.makedirs(folder)
                        print_success("Language successfully created.")
                    else:
                        print_wrong("Language already exists.\nAborting ...")
                elif action == "e":
                    break

            except ValueError:
                print_danger("ValueError Occurred.")

    except KeyboardInterrupt:
        print()
        print("Try command 'e' next time ;)")
    print("Hope you learned something today.")


if __name__ == '__main__':
    main()

