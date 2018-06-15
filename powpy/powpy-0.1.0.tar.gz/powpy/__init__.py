'''
A very simple Proof of work module, using SHA-256 hashes
'''
from re import match
from random import choice, randrange, getrandbits
import hashlib
from string import ascii_letters, digits

chars = ascii_letters + digits #abcde12345... etc.

def random_string():
    '''
    Return a random string, with a length from 1 to 1000 chars
    '''
    string = ''
    for i in range(randrange(1, 1000)):# random length
        string += choice(chars)# random chars
    return string

def make_hash(text):
    '''
    Convert a string into a SHA-256 hash
    '''
    m = hashlib.sha256()
    m.update(text.encode("utf-8"))
    return str(m.hexdigest())

def random_hash():
    '''
    Generate a random SHA-256 hash
    '''
    return make_hash(random_string())

def proof_of_work(initial_hash, difficult):
    '''
    Do a proof of work, using SHA-256 hashes.
    INPUT: An initial hash and a difficult (number of zeroes)
    OUTPUT: A new hash, depending of initial hash
    '''
    difficult = "0"*difficult# Set the number of zeroes (difficult)
    work = random_hash()# First attempt
    tries = 1
    while True:
        while not( match( difficult, make_hash( str(work + initial_hash) ) ) ):# Repeats until find a valid hash
            work = random_hash()
            tries += 1
        return work, make_hash( str(initial_hash + work) ), tries# Once the hash matches the requirements, return data