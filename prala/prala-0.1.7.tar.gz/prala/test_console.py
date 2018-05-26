import unittest
from prala.core import FilteredDictionary
from prala.core import Record
from prala import console

import itertools
from collections import Counter
import os
import sys

from unittest.mock import patch
from unittest.mock import MagicMock
from unittest.mock import Mock



class TestConsole(unittest.TestCase):
    BASE_NAME="testfile"
    DICT_FILE=BASE_NAME + "." + FilteredDictionary.DICT_EXT

    # Runs at the beginning of the test suit
    @classmethod
    def setUpClass(cls):
        content={
            "1":('v', 'group1', ['Abc', 'Adef', 'Aghij', 'Aklmnopq', 'A'], 'aaa' ),
            "2":('a', 'group1', ['Bcd', 'Befg', 'Bhijk'], 'bbb'),
            "3":('n', 'group1', ['Cde'], 'ccc'),
            "4":('b', 'group1', ['Def'], 'ddd')
        }

        # write into the test file the words
        with open( TestConsole.DICT_FILE, "w" ) as f:
            print(*[FilteredDictionary.RECORD_SPLITTER.join(
                [v[0]]+
                [v[1]]+
                [", ".join(v[2])]+
                [v[3]]
                ) for k, v in content.items()]
                , sep='\n', file=f)

    #Runs before every testcase
    def setUp(self): 
        pass

    
    def test_start( self ):
        os.urandom=MagicMock( return_value=3)   

        print("result: ", os.urandom())
        os.urandom()
        os.urandom()
        os.urandom.assert_called_once_with()


        """
        testargs = ["console", type(self).BASE_NAME ]
        with patch.object(sys, 'argv', testargs):

            #from prala.console import ConsolePrala
            #from unittest.mock import MagicMock
            #from unittest.mock import Mock

            #ConsolePrala.get_input=MagicMock(return_value="visszateres")
            #ConsolePrala.get_input=Mock(side_effect=BaseException( 'FOO' ) )
            console.main()
        """


    #Runs after every testcase - anyway	
    def tearDown(self): 
        pass

    # Runs at the end of the test suit
    @classmethod
    def tearDownClass(cls): 
        try:
            os.remove(TestConsole.DICT_FILE)
            os.remove(TestConsole.BASE_NAME+".bak")
            os.remove(TestConsole.BASE_NAME+".dat")
            os.remove(TestConsole.BASE_NAME+".dir")
        except Exception:
            # swallow the error if there is no such files
            pass


#if __name__ == "__main__":
#	unittest.main()

