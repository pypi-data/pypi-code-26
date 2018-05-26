import pyttsx3 as pyttsx
import shelve
import random
import numpy as np
import hashlib
import re
import os
from time import sleep
from prala.accessories import Enum
from prala.exceptions import EmptyDictionaryError
from prala.exceptions import NoDictionaryError

class FilteredDictionary(object):
    DICT_EXT=".dict"
    RECORD_SPLITTER=":"
    WORD_SPLITTER="|"

    DICT_POS=Enum(
        POS_POS_FILTER=0,
        POS_EXTRA_FILTER=1,
        POS_LEARNING=2,
        POS_BASE=3,
        POS_NOTE=4
    )

    RECORD_POS= Enum(
        POS_POS_FILTER=0,
        POS_LEARNING=1,
        POS_BASE=2,
        POS_NOTE=3,
    )

    def __init__(self, file_name, base_language, learning_language, part_of_speach_filter="", extra_filter=""):
        """
        Opens the dictionary, 
        selects the set of the words usin filter
        Opens the statistics file
        Pair the statistics to the words
        creates two instance variables:
            word_dict   <dictionary>
                            "id": ["part_of_speach", [word, and, its, forms], "base_word"]
            recent_stat_list <dictionary>
                            "id": [[1,0,0,1],[0, 0, 1]]
        """

        self.base_language=base_language
        self.learning_language=learning_language
        
        # if it does not ended to .dict, I append .dict to it
        name, ext = os.path.splitext( file_name )
        if ext != self.__class__.DICT_EXT:
            ext += self.__class__.DICT_EXT

        self.dict_file_name = name + ext
        self.stat_file_name = name

        #
        # collects POS list and extra filter list
        #
        self.pos_filter_list = [""]
        self.extra_filter_list = [""]

        #
        # read, parse and filter the necesarry words
        #
        # output: word_dict
        try:

            with open( self.dict_file_name ) as f:

                #
                # collect words by filters
                #
                self.word_dict={}
                for line in f:
                    
                    #id for the line
                    ln=hashlib.md5(line.encode()).hexdigest()                    

                    #pharse the line to a list
                    element_list=line.strip().split(self.__class__.RECORD_SPLITTER)
                    #fill up the list if it shorter
                    element_list= (element_list + [''] * type(self).DICT_POS.size())[:type(self).DICT_POS.size()]

                    # collects POS filters into list
                    # collects EXTRA filters into list
                    pf = element_list[type(self).DICT_POS.POS_POS_FILTER].lower()
                    if pf not in self.pos_filter_list:
                        self.pos_filter_list.append( pf )
                    
                    ef = element_list[type(self).DICT_POS.POS_EXTRA_FILTER].lower()
                    if ef not in self.extra_filter_list:
                        self.extra_filter_list.append( ef )

                    # filters the result by part_of_speech_filter and extra_filter
                    if (len(part_of_speach_filter) == 0 or element_list[type(self).DICT_POS.POS_POS_FILTER].lower() == part_of_speach_filter.lower()) and (len(extra_filter) == 0 or re.compile(extra_filter).search( element_list[type(self).DICT_POS.POS_EXTRA_FILTER] ) != None ):
                        #self.word_dict[str(ln)]=(element_list[type(self).POS_DICT_POS], element_list[type(self).POS_DICT_BASE], list(map(str.strip, element_list[type(self).POS_DICT_LEARNING].strip().split(self.__class__.WORD_SPLITTER) ) ) )

                        learning_word_list=list(map(str.strip, element_list[type(self).DICT_POS.POS_LEARNING].strip().split(self.__class__.WORD_SPLITTER) ) )

                        # if there is BASE word and LEARNING words
                        if element_list[type(self).DICT_POS.POS_BASE] and all(learning_word_list):
                            self.word_dict[str(ln)] = [None] * type(self).RECORD_POS.size()
                            self.word_dict[str(ln)][type(self).RECORD_POS.POS_POS_FILTER] = element_list[type(self).DICT_POS.POS_POS_FILTER] 
                            self.word_dict[str(ln)][type(self).RECORD_POS.POS_LEARNING] = learning_word_list
                            self.word_dict[str(ln)][type(self).RECORD_POS.POS_BASE] = element_list[type(self).DICT_POS.POS_BASE]                            
                            self.word_dict[str(ln)][type(self).RECORD_POS.POS_NOTE] = element_list[type(self).DICT_POS.POS_NOTE] 

                # if the word list is empty the there is nothing to do
                if len(self.word_dict) == 0:
                    raise EmptyDictionaryError( self.dict_file_name, part_of_speach_filter, extra_filter)
                    #print( "The dict is empty ..." )
                    #exit()

        except FileNotFoundError as e:
            raise NoDictionaryError(e)

        
        #now in the word_dict found all filtered words by line

        with shelve.open(self.stat_file_name, writeback=True) as db:

            #
            # get the statistics for the filtered word list
            #
            # output: db
            self.recent_stat_list={}

            for word_id, _ in self.word_dict.items():

                # create the record if it does not exist
                try:

                    # remove all empty tuples
                    db[word_id] = [t for t in db[word_id] if not all(t)]

                except Exception as e:

                    #as there has not been record creates an empty
                    db[word_id] = []
    
                #append the actual empty list for statistics
                db[word_id].append([])
    
                #updates
                self.recent_stat_list[word_id]=db[word_id][-1]   


    def get_next_random_record(self, wrong_record=None):
        """
        Gives back a randomly chosen line object from the filtered wordlist

        input:  wrong_record 
                    - It is unrelevant until all words was answerd 
                    - If it is EMPTY then the chance depends on the points
                    - If it is NOT EMPTY the the same question will be asked until it answered

        output: WordLine object
        """
        
        # calculates the next id to ask
        word_id=self.get_random_id(self.recent_stat_list, wrong_record)

        # returns the word with the calculated id to ask
        return Record( self.base_language, self.learning_language, word_id, self.word_dict[ word_id ], self.recent_stat_list[ word_id ])
        #return word_id, self.word_dict[ word_id ]

    def add_result_to_stat(self, word_id, success):
        """
        input:  word_id: string
                success: boolean
                    True    -good user_answer
                    False   -wrong anser
        """
        with shelve.open(self.stat_file_name, writeback=True) as db:

            """
            #updates db
            db[word_id][-1].append(1 if success else 0)
            #updates recent_stat_list variable
            self.recent_stat_list[word_id]=db[word_id][-1]
            """

            #updates db
            self.recent_stat_list[word_id].append(1 if success else 0)

            #updates recent_stat_list variable
            db[word_id][-1]=self.recent_stat_list[word_id]

    def get_random_id(self, stat_list, wrong_record=None):
        """
        Returns the identifier of a random word in the list.
        The word with higher points get higher chance to be selected.
        The points depend on the good and bad answers

        input: 
                stat_list - [dictionary]    key:    word id
                                            value:  []
                wrong_record - [record]
                    - It is unrelevant until all words was answerd
                    - If it is EMPTY then the chance depends on the points
                    - If it is NOT EMPTY the the same question will be asked until it answered
        output:
                a random word id from the list
        """
        #empty if every element have at least one 1 in the list
        first_round_list=[i for i in stat_list if not any(stat_list[i])]

        #if not empty
        if any(first_round_list):

            #all element with same chance - must be changed
            return random.choice(first_round_list)
    
        # if the wrong_record parameter is NOT empty
        elif not wrong_record == None:

            # then it must ask again the same word (record)
            return wrong_record.word_id

        #if empty - chances must be taken by statistics
        else:
            return random.choice([ k for k, v in stat_list.items() for i in range(self.get_points(v))])

    def get_points(self, recent_stat):
        """
        Calculates the points of the "recent_stat" list
        "recent_stat" contains 0s and 1s representing the bad and good answers
        for a specific word in the recent session.
        More points mean worse answers.
        The following generate points:
            -less questioned higher points
            -number of the tralling 0s
            -number of the wrong answers
            -number of the wrong answers after a good user_answer
    
        input:
                [list]: recent_stat: 
                            -   0: bad user_answer
                            -   1: good user_answer
        """
        points=1

        #shorter list has more points (longest list size-number of 1s in this list)
        points += max([len(v) for k, v in self.recent_stat_list.items()])-sum(recent_stat)
        
        # counts not knowing last n times(ends with 0)
        #points += len(recent_stat)-len("".join(map(str, recent_stat)).rstrip("0"))    
        
        # counts not knowing last-1 n times (the last is ignored)
        #points += len(recent_stat[0:-1])-len("".join(map(str, recent_stat[0:-1])).rstrip("0"))    

        # counts not knowing last-1 n times (the last is ignored) or last n times
        points += max(
            len(recent_stat)-len("".join(map(str, recent_stat)).rstrip("0")),
            len(recent_stat[0:-1])-len("".join(map(str, recent_stat[0:-1])).rstrip("0"))
        )

        # counts difference between 1 and 0
        points += max(sum([1 for i in recent_stat if i == 0])*2 - len(recent_stat), 0)

        # counts all forgettings (1 -> 0)
        points += np.sum(np.diff(recent_stat) == -1)          

        return points

    def get_recent_stat_list(self):
        """
        Gives back the statistics of the last cycle

        output: [tuple]
                        tuple[0]:   numbers of the asked questions
                        tuple[1]:   numbers of the good answers
                        tuple[2]:   numbers of not asked questions (all questions-good answers)
        """
        full_list=[ i for k, v in self.recent_stat_list.items() for i in v]
        return(len(full_list), sum(full_list), max(0, len(self.recent_stat_list)-sum(full_list)))

    def getPOSFilterList(self):
        return self.pos_filter_list

    def getExtraFilterList(self):
        return self.extra_filter_list

    def setBaseLanguage(self, language):
        self.base_language = language

    def setLearningLanguage(self, language):
        self.learning_language = language        

class Record(object):

    def __init__(self, base_language, learning_language, word_id, word, recent_stat):
        """
            base_language       - string
            learning_language   - string
            word_id             - integer
            word                - list:     [part_of_speach, [word, and, its, forms], base_word, note]
        """
        self.base_language = base_language
        self.learning_language = learning_language
        self.word_id = word_id
        
        self.part_of_speach = word[FilteredDictionary.RECORD_POS.POS_POS_FILTER]
        self.learning_words = word[FilteredDictionary.RECORD_POS.POS_LEARNING]
        self.base_word = word[FilteredDictionary.RECORD_POS.POS_BASE]
        self.note = word[FilteredDictionary.RECORD_POS.POS_NOTE]

         #self.word = word
        self.recent_stat = recent_stat

    def get_recent_stat(self):
        """
        Gives back the recent statistics of the actual Record

        output: tuple of recent statistics (1,0,0,1)                    
        """
        return self.recent_stat

    def check_answer(self, user_answer):
        """
        input:  user_answer: list
                    ['word', 'and', 'its', 'forms']

        output: boolean
                    True:   if the user_answer is acceptable
                    False:  if the user_answer is not acceptable
                list
                    [first, wrong, position, of, words]
        """
        zipped_list= list(zip( self.learning_words + [" "*len(i) for i in user_answer][len(self.learning_words):], user_answer + [" "*len(i) for i in self.learning_words][len(user_answer):] ) )
        zipped_list=[ (i[0] + (" "*len(i[1]))[len(i[0]):], i[1] + (" "*len(i[0]))[len(i[1]):] ) for i in zipped_list]

        # equalancy independent of the lower case/upper case
        diff_list=[[i for i in range(len(j[1])) if j[1][i].lower() != j[0][i].lower()] for j in zipped_list]
        if sum([1 for i in diff_list if len(i)!=0]) == 0:
            return True, diff_list
        else:
            return False, diff_list

    def say_out_base(self):
        """
        It says out the text in the list on the 'base language'
        """
        engine = pyttsx.init()
        engine.setProperty('voice', self.base_language)		#voice id
        #engine.setProperty('rate', 150)
        #engine.setProperty('volume', 1)
    
        #while engine.isBusy():
        #    sleep(0.5)

        #TODO parameter to ENUM
        engine.say(self.base_word)
        engine.runAndWait()

    def say_out_learning(self):
        """
        It says out the text in the list on the 'learning language'
        """
        engine = pyttsx.init()

        engine.setProperty('voice', self.learning_language)		#voice id
        
        #TODO parameter to ENUM
        [engine.say(i) for i in self.learning_words]
        engine.runAndWait()

    def setBaseLanguage(self, language):
        self.base_language = language

    def setLearningLanguage(self, language):
        self.learning_language = language

#if __name__ == "__main__":
    #myFiteredDictionary=FiteredDictionary()
    #print(myFiteredDictionary.get_next())
