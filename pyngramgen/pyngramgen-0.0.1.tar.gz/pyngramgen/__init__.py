#!/usr/bin/python
import os
import sys
import math
import itertools

class PyNgramGen(object): 
    """
    main class
    """
    def __init__(self, n, acc_chars): 
        if not isinstance(n, int) or n < 2:
            raise Exception('param error')
        self.accepted_chars = acc_chars
        self.pos = {}
        self.gram = n
        self.pos = [i for i in self.accepted_chars]
        for i in xrange(self.gram - 1):
            self.pos  = [''.join(i) for i in\
            itertools.product(self.pos, self.accepted_chars)]
        self.pos = dict([(char, idx) for idx, char in enumerate(self.pos)])

    def __normalize(self, line):
        return [c.lower() for c in line if c.lower() in self.accepted_chars]
    
    def generator(self, l):
        """ Return all n grams from l after normalizing """
        filtered = self.__normalize(l)
        for start in range(0, len(filtered) - self.gram + 1):
            s = ''.join(filtered[start:start + self.gram])
            yield s,self.pos[s]
    
if __name__ == '__main__':
    if len(sys.argv) != 2: 
        print "python %s n" % (sys.argv[0])
        quit()
    while True: 
        iput = raw_input()
        obj = PyNgramGen(int(sys.argv[1]), 'abcdefghijklmnopqrstuvwxyz')
        for i in obj.generator(iput):
            print i
