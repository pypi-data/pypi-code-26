import unittest
from unittest.mock import patch

import itertools
from collections import Counter
import os

from prala.core import FilteredDictionary
from prala.core import Record

class TestWordCycleFunctions(unittest.TestCase):
    BASE_NAME="testfile"
    DICT_FILE=BASE_NAME + "." + FilteredDictionary.DICT_EXT

    # Runs at the beginning of the test suit
    @classmethod
    def setUpClass(cls):
        """
        Creates a dict file with different content
        """
        content={
            "1":('v', 'group1', ['Abc', 'Adef', 'Aghij', 'Aklmnopq', 'A'], 'aaa' ),
            "2":('a', 'group1', ['Bcd', 'Befg', 'Bhijk'], 'bbb'),
            "3":('n', 'group1', ['Cde'], 'ccc'),
            "4":('b', 'group1', ['Def'], 'ddd')
        }

        # write into the test file the words
        with open( TestWordCycleFunctions.DICT_FILE, "w" ) as f:
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
        #self.myFilteredDictionary=FilteredDictionary(TestWordCycleFunctions.BASE_NAME, 'hungarian', 'swedish') 

    def test_get_points_same_size_stat( self ):
        """
        Tests if a list of statistics have back the right points.
        The list and the expected points are the following:
            (0, 0, 0)->10
            (0, 0, 1)->6
            (0, 1, 0)->6
            (0, 1, 1)->2
            (1, 0, 0)->7
            (1, 0, 1)->4
            (1, 1, 0)->4
            (1, 1, 1)->1
        """
        # Mock the __ini__
        with patch.object(FilteredDictionary, "__init__", lambda x: None):
            myFilteredDictionary=FilteredDictionary()
            myFilteredDictionary.base_language="hungarian"
            myFilteredDictionary.learning_language="swedish"
            myFilteredDictionary.recent_stat_list={i:list(i) for i in list(itertools.product([0,1], repeat=3))}
            myFilteredDictionary.word_dict={
                "1":('v', ['AAA'], 'aaa', ''),
                "2":('v', ['BBB'], 'bbb', ''),
                "3":('v', ['CCC'], 'ccc', ''),
                "4":('v', ['DDD'], 'ddd', ''),
                "5":('v', ['EEE'], 'aaa', ''),
                "6":('v', ['FFF'], 'bbb', ''),
                "7":('v', ['GGG'], 'ccc', ''),
                "8":('v', ['HHH'], 'ddd', '')
            }
            expected_list=[10,6,6,2,7,4,4,1]
            # run with all statuses -> result zipped with the expected valus -> pairs substracted from each other -> sum -> it must be 0
            self.assertEqual( sum( [ j[0]-j[1] for j in zip( [myFilteredDictionary.get_points(i) for i in myFilteredDictionary.recent_stat_list], expected_list) ] ), 0 )
            #print()
            #print(*[str(k) + "->" + str(myFilteredDictionary.get_points(v)) for k,v in myFilteredDictionary.recent_stat_list.items()], sep="\n")


    def test_get_points_different_size_stat( self ):
        """
        Tests if a list of statistics have back the right points.
        The list and the expected points are the following:
            (0,)->6
            (1,)->3
            (0, 0)->8
            (0, 1)->4
            (1, 0)->5
            (1, 1)->2
            (0, 0, 0)->10
            (0, 0, 1)->6
            (0, 1, 0)->6
            (0, 1, 1)->2
            (1, 0, 0)->7
            (1, 0, 1)->4
            (1, 1, 0)->4
            (1, 1, 1)->1
        """
        # Mock the __ini__
        with patch.object(FilteredDictionary, "__init__", lambda x: None):
            myFilteredDictionary=FilteredDictionary()
            myFilteredDictionary.base_language="hungarian"
            myFilteredDictionary.learning_language="swedish"
            myFilteredDictionary.recent_stat_list={i:list(i) for i in list(itertools.product([0,1], repeat=1)) + list(itertools.product([0,1], repeat=2)) + list(itertools.product([0,1], repeat=3))}
            myFilteredDictionary.word_dict={"1":('v', ['AAA'], 'aaa', '') }
            expected_list=[6,3,8,4,5,2,10,6,6,2,7,4,4,1]
            # run with all statuses -> result zipped with the expected valus -> pairs substracted from each other -> sum -> it must be 0
            self.assertEqual( sum( [ j[0]-j[1] for j in zip( [myFilteredDictionary.get_points(i) for i in myFilteredDictionary.recent_stat_list], expected_list) ] ), 0 )
            #print()
            #print(*[str(k) + "->" + str(myFilteredDictionary.get_points(v)) for k,v in myFilteredDictionary.recent_stat_list.items()], sep="\n")


    def test_get_random_id_equal_chances_all( self ):
        """
        Tests if there is about 50%/50% chance to get the words
        which had not got good answer yet
        """
        self.myFilteredDictionary=FilteredDictionary(TestWordCycleFunctions.BASE_NAME, 'hungarian', 'swedish') 
        
        stat_list={
            "a": [0,0,0],   # no good answer
            "b": [0,0,0],   # no good answer
        } 

        result=Counter( [self.myFilteredDictionary.get_random_id(stat_list) for i in range(40000)] )
        self.assertAlmostEqual( result["b"] / result["a"], 1.0, delta=0.08)

    def test_get_random_id_equal_chances_some( self ):
        """
        Tests if there is 0.0% chance to get the word
        which had got a good answer
        """

        self.myFilteredDictionary=FilteredDictionary(TestWordCycleFunctions.BASE_NAME, 'hungarian', 'swedish') 
        
        stat_list={
            "a": [0,0,0],   # no good answer
            "b": [0,1,0],   # there was 1 good answer
        }

        result=Counter( [self.myFilteredDictionary.get_random_id(stat_list) for i in range(40000)] )
        self.assertAlmostEqual( result["b"] / result["a"], 0.0, delta=0.0)

    def test_get_random_id_wighted_chance( self ):
        """
        Tests if the chance to get the words
        are proportional to the point (weight) what they have.
        """
       # Mock the __ini__
        with patch.object(FilteredDictionary, "__init__", lambda x: None):
            myFilteredDictionary=FilteredDictionary()
            myFilteredDictionary.base_language="hungarian"
            myFilteredDictionary.learning_language="swedish"
            myFilteredDictionary.recent_stat_list={
                "a": [1,1,1],   # 1 point  (weight)
                "b": [0,1,1],   # 2 points (weight)
            }
            myFilteredDictionary.word_dict={
                "1":('v', ['AAA'], 'aaa', ''),
                "2":('v', ['BBB'], 'aaa', '')             
            }

            result=Counter( [myFilteredDictionary.get_random_id(myFilteredDictionary.recent_stat_list) for i in range(40000)] )
            self.assertAlmostEqual( result["b"] / result["a"], 2.0, delta=0.08)

    def test_get_next_random_record_only_one_good_answer( self ):
        """
        Tests if there is about same chance to get the words
        which had not got good answer yet
        """

        # Mock the __ini__
        with patch.object(FilteredDictionary, "__init__", lambda x: None):
            myFilteredDictionary=FilteredDictionary()
            myFilteredDictionary.base_language="hungarian"
            myFilteredDictionary.learning_language="swedish"
            myFilteredDictionary.recent_stat_list={
                "1":[0,0,0],
                "2":[0,0,0],
                "3":[0,1,0],
                "4":[0,0,0],
            }
            myFilteredDictionary.word_dict={
                "1":('v', ['AAA'], 'aaa', ''),
                "2":('v', ['BBB'], 'bbb', ''),
                "3":('v', ['CCC'], 'ccc', ''),
                "4":('v', ['DDD'], 'ddd', '')
            }

            loop=300000
            result=Counter([myFilteredDictionary.get_next_random_record().base_word for i in range(loop)])
            self.assertAlmostEqual( loop/3, result['aaa'], delta=600)
            self.assertAlmostEqual( loop/3, result['bbb'], delta=600)
            self.assertAlmostEqual( 0.0, result['ccc'], delta=0)
            self.assertAlmostEqual( loop/3, result['ddd'], delta=600)

    def test_get_next_has_good_answer( self ):
        """
        Tests if the chance to get the words
        are proportional to the point (weight) what they have.
        It means: 10%/20%/30%/40% in sequence
        """

        # Mock the __ini__
        with patch.object(FilteredDictionary, "__init__", lambda x: None):
            myFilteredDictionary=FilteredDictionary()
            myFilteredDictionary.base_language="hungarian"
            myFilteredDictionary.learning_language="swedish"
            myFilteredDictionary.recent_stat_list={
                "1":[1,1,1],    # 1 point => 1/20 probability
                "2":[0,1,1],    # 2 points => 2/20 probability
                "3":[1,0,1],    # 4 points => 4/20 probability
                "4":[0,1,0],    # 6 points => 6/20 probability
                "5":[1,0,0],    # 7 points => 7/20 probability
            }
            myFilteredDictionary.word_dict={
                "1":('v', ['AAA'], 'aaa', ''),
                "2":('v', ['BBB'], 'bbb', ''),
                "3":('v', ['CCC'], 'ccc', ''),
                "4":('v', ['DDD'], 'ddd', ''),
                "5":('v', ['EEE'], 'eee', '')
            }

            loop=40000

            result=Counter([myFilteredDictionary.get_next_random_record().base_word for i in range(loop)])

            self.assertAlmostEqual(result['aaa']/loop, 1/20, delta=0.01)
            self.assertAlmostEqual(result['bbb']/loop, 2/20, delta=0.01)
            self.assertAlmostEqual(result['ccc']/loop, 4/20, delta=0.01)
            self.assertAlmostEqual(result['ddd']/loop, 6/20, delta=0.01)
            self.assertAlmostEqual(result['eee']/loop, 7/20, delta=0.01)
    
    def test_check_answer_true( self ):
        """
        Checks if I get True return and empty differece list 
        when all answer equals to the base
        """
        
        self.myFilteredDictionary=FilteredDictionary(TestWordCycleFunctions.BASE_NAME, 'hungarian', 'swedish', part_of_speach_filter='v') 
        
        answer=['Abc', 'Adef', 'Aghij', 'Aklmnopq', 'A']
        result=self.myFilteredDictionary.get_next_random_record().check_answer(answer)
        self.assertTrue(result[0])
        self.assertEqual(sum([1 for i in result[1] if len(i) != 0]), 0 )
 
    def test_check_answer_false_shorter_list( self ):
        """
        Checks if I get False return and the corresponding difference list
        when some answers are different to the bases
        """

        self.myFilteredDictionary=FilteredDictionary(TestWordCycleFunctions.BASE_NAME, 'hungarian', 'swedish', part_of_speach_filter='v') 
        
        answer=['Adc', 'Adef', 'Adhlj', 'Aklmnopq']
        result=self.myFilteredDictionary.get_next_random_record().check_answer(answer)
        self.assertFalse(result[0])
        self.assertEqual(result[1][0],[1])
        self.assertEqual(result[1][1],[])
        self.assertEqual(result[1][2],[1,3])
        self.assertEqual(result[1][4],[0])

    def test_check_answer_false_longer_list( self ):
        """
        Checks if I get False return and the corresponding difference list
        when the answer list is longer than the base
        """

        self.myFilteredDictionary=FilteredDictionary(TestWordCycleFunctions.BASE_NAME, 'hungarian', 'swedish', part_of_speach_filter='v') 
        
        answer=['Abc', 'Adef', 'Aghij', 'Aklmnopq', 'A', 'Abcd']
        result=self.myFilteredDictionary.get_next_random_record().check_answer(answer)
        self.assertFalse(result[0])
        self.assertEqual(result[1][0],[])
        self.assertEqual(result[1][1],[])
        self.assertEqual(result[1][2],[])
        self.assertEqual(result[1][3],[])
        self.assertEqual(result[1][4],[])
        self.assertEqual(result[1][5],[0, 1, 2, 3])

    def test_check_answer_false_shorter_answer( self ):
        """
        Checks if I get False return and the corresponding difference list
        when the answer list has at least one shorter answer than the base
        """
        
        self.myFilteredDictionary=FilteredDictionary(TestWordCycleFunctions.BASE_NAME, 'hungarian', 'swedish', part_of_speach_filter='v') 
        
        answer=['Abc', 'Adef', 'Agh', 'Aklmnopq', 'A']
        result=self.myFilteredDictionary.get_next_random_record().check_answer(answer)
        self.assertFalse(result[0])
        self.assertEqual(result[1][0],[])
        self.assertEqual(result[1][1],[])
        self.assertEqual(result[1][2],[3,4])
        self.assertEqual(result[1][3],[])
        self.assertEqual(result[1][4],[])

    def test_check_answer_false_longer_answer( self ):
        """
        Checks if I get False return and the corresponding difference list
        when the answer list has at least one longer answer than the base
        """        
        self.myFilteredDictionary=FilteredDictionary(TestWordCycleFunctions.BASE_NAME, 'hungarian', 'swedish', part_of_speach_filter='v')
        answer=['Abc', 'Adef', 'Aghijkl', 'Aklmnopq', 'A']
        result=self.myFilteredDictionary.get_next_random_record().check_answer(answer)
        self.assertFalse(result[0])
        self.assertEqual(result[1][0],[])
        self.assertEqual(result[1][1],[])
        self.assertEqual(result[1][2],[5,6])
        self.assertEqual(result[1][3],[])
        self.assertEqual(result[1][4],[])

    def test_check_answer_false_empty_answer( self ):
        """
        Checks if I get False return and the corresponding difference list
        when the answer list has at least one empty answer
        """        
        self.myFilteredDictionary=FilteredDictionary(TestWordCycleFunctions.BASE_NAME, 'hungarian', 'swedish', part_of_speach_filter='v')
        answer=['Abc', '', 'Aghij', 'Aklmnopq', 'A']
        result=self.myFilteredDictionary.get_next_random_record().check_answer(answer)
        self.assertFalse(result[0])
        self.assertEqual(result[1][0],[])
        self.assertEqual(result[1][1],[0,1,2,3])
        self.assertEqual(result[1][2],[])
        self.assertEqual(result[1][3],[])
        self.assertEqual(result[1][4],[])

    def test_recent_stat_of_one_word( self ):
        """
        Tests if the get_recent_stat() method gives back the right values
        """
        self.myFilteredDictionary=FilteredDictionary(TestWordCycleFunctions.BASE_NAME, 'hungarian', 'swedish', part_of_speach_filter='v') 
        
        record=self.myFilteredDictionary.get_next_random_record()
        self.myFilteredDictionary.add_result_to_stat(record.word_id, True)
        self.myFilteredDictionary.add_result_to_stat(record.word_id, False)
        self.myFilteredDictionary.add_result_to_stat(record.word_id, True)
        self.assertEqual( record.get_recent_stat(), [1,0,1] )
       
    def test_recent_stat_of_all_words(self):
        """
        Tests if the get_recent_stat_list() method gives back the right values
        """
        self.myFilteredDictionary=FilteredDictionary(TestWordCycleFunctions.BASE_NAME, 'hungarian', 'swedish', part_of_speach_filter='') 
        
        record=self.myFilteredDictionary.get_next_random_record()
        self.myFilteredDictionary.add_result_to_stat(record.word_id, False)
        self.myFilteredDictionary.add_result_to_stat(record.word_id, True)

        record=self.myFilteredDictionary.get_next_random_record()
        self.myFilteredDictionary.add_result_to_stat(record.word_id, False)
        self.myFilteredDictionary.add_result_to_stat(record.word_id, False)
        self.myFilteredDictionary.add_result_to_stat(record.word_id, True)

        record=self.myFilteredDictionary.get_next_random_record()
        self.myFilteredDictionary.add_result_to_stat(record.word_id, False)
        self.myFilteredDictionary.add_result_to_stat(record.word_id, False)
        self.myFilteredDictionary.add_result_to_stat(record.word_id, False)
        self.myFilteredDictionary.add_result_to_stat(record.word_id, True)

        record=self.myFilteredDictionary.get_next_random_record()
        self.myFilteredDictionary.add_result_to_stat(record.word_id, False)
        self.myFilteredDictionary.add_result_to_stat(record.word_id, False)
        self.myFilteredDictionary.add_result_to_stat(record.word_id, False)
        self.myFilteredDictionary.add_result_to_stat(record.word_id, False)

        res_stat=self.myFilteredDictionary.get_recent_stat_list()
        self.assertEqual(res_stat[0], 13)
        self.assertEqual(res_stat[1], 3)
        self.assertEqual(res_stat[2], 1)

    def test_there_is_only_base_word(self):
        pass

    def _test_say_out_base(self):
        self.myFilteredDictionary=FilteredDictionary(TestWordCycleFunctions.BASE_NAME, 'hungarian', 'swedish', part_of_speach_filter='v') 
        self.myFilteredDictionary.get_next_random_record().say_out_base()

    def _test_say_out_learning(self):
        self.myFilteredDictionary=FilteredDictionary(TestWordCycleFunctions.BASE_NAME, 'hungarian', 'swedish', part_of_speach_filter='v') 
        self.myFilteredDictionary.get_next_random_record().say_out_learning()

    #Runs after every testcase - anyway	
    def tearDown(self): 
        pass

    # Runs at the end of the test suit
    @classmethod
    def tearDownClass(cls): 
        """
        Removes the dict file and the generated stat files
        """
        os.remove(TestWordCycleFunctions.DICT_FILE)
        os.remove(TestWordCycleFunctions.BASE_NAME+".bak")
        os.remove(TestWordCycleFunctions.BASE_NAME+".dat")
        os.remove(TestWordCycleFunctions.BASE_NAME+".dir")

(7, [0, 0, 0]), 
(2, [0, 0, 1]), 
(4, [0, 1, 0]), 
(1, [0, 1, 1]), 
(5, [1, 0, 0]), 
(2, [1, 0, 1]), 
(3, [1, 1, 0]), 
(1, [1, 1, 1])

#if __name__ == "__main__":
#    unittest.main()

def run_tests():  
    print(__name__)  
    input()
    unittest.main()

if __name__ == '__main__':
    unittest.main()