# -*- coding: utf-8 -*-
"""
Created on Tue Jun  5 12:27:49 2018

@author: imarshal
"""

import unittest
import cards

class TestCases(unittest.TestCase):

    def test_std_deck_as_text(self):
        d1 = cards.Deck()
        s = ("1D | 2D | 3D | 4D | 5D | 6D | 7D | 8D | 9D | 10D | 11D | 12D | 13D | "
             "1C | 2C | 3C | 4C | 5C | 6C | 7C | 8C | 9C | 10C | 11C | 12C | 13C | "
             "1H | 2H | 3H | 4H | 5H | 6H | 7H | 8H | 9H | 10H | 11H | 12H | 13H | "
             "1S | 2S | 3S | 4S | 5S | 6S | 7S | 8S | 9S | 10S | 11S | 12S | 13S")
        self.assertEqual(d1.deck_as_text(),s, "Standard deck doesn't print correctly")
    def test_deck_comparison(self):
        d1 = cards.Deck()
        d2 = cards.Deck()
        self.assertEqual(d1, d2, "Deck comparison operator fails on 2 standard decks")
    def test_shuffle_full_deck(self):
        d1 = cards.Deck()
        d2 = cards.Deck()
        d2.shuffle_deck()
        self.assertNotEqual(d1, d2, "Shuffled deck did not change") #might not be the perfect test case,
        #but statistically nearly impossible to shuffle deck back order
    def test_shuffle_then_order_full_deck(self):
        d1 = cards.Deck()
        d2 = cards.Deck()
        d2.shuffle_deck()
        d2.order_deck()
        self.assertEqual(d1, d2, "Shuffled deck did not reorder on order() call")
    def test_get_suit_from_std_deck(self):
        d1 = cards.Deck()
        diamond_string = "1D | 2D | 3D | 4D | 5D | 6D | 7D | 8D | 9D | 10D | 11D | 12D | 13D"
        club_string = "1C | 2C | 3C | 4C | 5C | 6C | 7C | 8C | 9C | 10C | 11C | 12C | 13C"
        heart_string = "1H | 2H | 3H | 4H | 5H | 6H | 7H | 8H | 9H | 10H | 11H | 12H | 13H"
        spade_string = "1S | 2S | 3S | 4S | 5S | 6S | 7S | 8S | 9S | 10S | 11S | 12S | 13S"
        diamond_deck = d1.get_suit("Diamond")
        club_deck = d1.get_suit("Club")
        heart_deck = d1.get_suit("Heart")
        spade_deck = d1.get_suit("Spade")
        self.assertEqual(diamond_deck.deck_as_text(),diamond_string, "get_suit() failed Diamond")
        self.assertEqual(club_deck.deck_as_text(),club_string, "get_suit() failed Club")
        self.assertEqual(heart_deck.deck_as_text(),heart_string, "get_suit() failed Heart")
        self.assertEqual(spade_deck.deck_as_text(),spade_string, "get_suit() failed Spade")



if __name__ == '__main__':
    unittest.main()