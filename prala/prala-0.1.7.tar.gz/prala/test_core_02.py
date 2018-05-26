import unittest
from prala.core import FilteredDictionary
from prala.core import Record
from prala.exceptions import EmptyDictionaryError
from prala.exceptions import NoDictionaryError

import prala.accessories as acc

import itertools
from collections import Counter
import os

from unittest.mock import patch

class TestWordCycleInit(unittest.TestCase):
    BASE_NAME="testfile"
    DICT_FILE=BASE_NAME + "." + FilteredDictionary.DICT_EXT

    # Runs at the beginning of the test suit
    @classmethod
    def setUpClass(cls):
        """
        Creates a dict file with 
        -no learning words
        -no base word
        -empty lines
        And all possible combitanions
        """
        content={
            "1":('v', 'group1', [''], 'aaa', ''),
            "2":('a', 'group1', ['Bcd'], '', ''),
            "3":('a', 'group1', [''], '', ''),
            "4":('', '', [''], '', ''),
            "5":('b', 'group1', ['Def'], 'ddd', ''),
            "6":('b', 'group1', ['Hjk'], 'www', 'note', '')
        }

        # write into the test file the words
        with open( TestWordCycleInit.DICT_FILE, "w" ) as f:
            print("", file=f)
            print(*[FilteredDictionary.RECORD_SPLITTER.join(
                [v[0]]+
                [v[1]]+
                [", ".join(v[2])]+
                [v[3]]+
                [v[4]]
                ) for k, v in content.items()]
                , sep='\n', file=f)
            print("   ", file=f)

    #Runs before every testcase
    def setUp(self): 
        pass
 
    def test_no_words_at_all( self ):
        """
        Tests if there was no word found
        """        
        #self.assertRaises(EmptyDictionaryError, FilteredDictionary, TestWordCycleInit.BASE_NAME, 'hungarian', 'swedish', part_of_speach_filter="blabla" )

        # when EmptyDictionaryError raised, no Exception raised in this test case
        # otherwise AsserionError raised
        with self.assertRaises(EmptyDictionaryError) as context:
            FilteredDictionary(TestWordCycleInit.BASE_NAME, 'hungarian', 'swedish', part_of_speach_filter="blabla")
 
    def test_no_base_no_learning_words( self ):
        """
        The line int the dict file will be avoided which are:
        -empty
        -has no base word
        -has no learning word
        """
        expected_list=[
            ['6cb08b08a1b3145f1a7a1de2983daa8f', 'b', ['Def'], 'ddd', ''],
            ['18223d6b04accdd8ef610ee7a566dd6a', 'b', ['Hjk'], 'www', 'note']
        ]
        
        myFilteredDictionary=FilteredDictionary(TestWordCycleInit.BASE_NAME, 'hungarian', 'swedish') 
        result_list=[[k,*v] for k, v in myFilteredDictionary.word_dict.items()]
        for j in range(len(expected_list)):
            
            self.assertEqual( expected_list[j], result_list[j])            

    def tearDown(self): 
        pass

    # Runs at the end of the test suit
    @classmethod
    def tearDownClass(cls): 
        """
        Deletes the dict file and the generated stat files
        """
        os.remove(TestWordCycleInit.DICT_FILE)
        os.remove(TestWordCycleInit.BASE_NAME+".bak")
        os.remove(TestWordCycleInit.BASE_NAME+".dat")
        os.remove(TestWordCycleInit.BASE_NAME+".dir")
        pass
