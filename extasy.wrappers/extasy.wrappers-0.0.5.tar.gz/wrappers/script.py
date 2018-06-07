#!/usr/bin/python
'''
Class that implements a simple approach to creating and running scripts
 - e.g. may be of use to run tleap or ptraj from within a python script.
'''
import subprocess
import tempfile
class Script:
    def __init__(self,filename=None):
        '''
        Initialise a new script. Scripts are just lines of text, that in
        the end will be run through some form of subprocess call. If no
        filename is specified, an 'anonymous' temporary file will be
        created (in the end - this doesn't happen until the run() method
        is called).
        '''
        self.filename = filename
        self.stringlist = []

    def append(self, string):
        '''
        Appends a new line of text to the script
        '''
        self.stringlist.append(string)

    def run(self, runcmd):
        '''
        Run the script, in the context of the given run command. This is a
        special string the will contain a reference to the script file in
        the form of a token "{}". For example, if runcmd = "cat {}", then
        the script would be listed. Any output from the command is returned
        as a string.
        '''
        # first save the script file. If no name was specified at the time
        # of creation, use a temporary file.
        if self.filename is not None:
            with open(self.filename,'w') as f:
                for line in self.stringlist:
                    f.write(line+'\n')

            rcmd = runcmd.format(self.filename)
            try:
                out = subprocess.check_output(rcmd.split(),stderr=subprocess.STDOUT)
                return out
            except subprocess.CalledProcessError as e:
                print e.output
                raise
        else:
            with tempfile.NamedTemporaryFile() as temp:
                for line in self.stringlist:
#                    print (line+'\n')
                    temp.write(line+'\n')

                temp.flush()
                rcmd = runcmd.format(temp.name)
                try:
                    out = subprocess.check_output(rcmd.split(),stderr=subprocess.STDOUT)
                    return out
                except subprocess.CalledProcessError as e:
                    print e.output
                    raise
