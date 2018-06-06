import unittest
import cards

class TestCases(unittest.TestCase):

    def test_std_deck_as_text(self):
        d1 = cards.Deck()
        s = ("AD | 2D | 3D | 4D | 5D | 6D | 7D | 8D | 9D | 10D | JD | QD | KD | "
             "AC | 2C | 3C | 4C | 5C | 6C | 7C | 8C | 9C | 10C | JC | QC | KC | "
             "AH | 2H | 3H | 4H | 5H | 6H | 7H | 8H | 9H | 10H | JH | QH | KH | "
             "AS | 2S | 3S | 4S | 5S | 6S | 7S | 8S | 9S | 10S | JS | QS | KS")
        sv = ("Ace of Diamonds | 2 of Diamonds | 3 of Diamonds | 4 of Diamonds | "
              "5 of Diamonds | 6 of Diamonds | 7 of Diamonds | 8 of Diamonds | "
              "9 of Diamonds | 10 of Diamonds | Jack of Diamonds | Queen of Diamonds | "
              "King of Diamonds | Ace of Clubs | 2 of Clubs | 3 of Clubs | 4 of Clubs | "
              "5 of Clubs | 6 of Clubs | 7 of Clubs | 8 of Clubs | 9 of Clubs | 10 of Clubs | "
              "Jack of Clubs | Queen of Clubs | King of Clubs | Ace of Hearts | 2 of Hearts | "
              "3 of Hearts | 4 of Hearts | 5 of Hearts | 6 of Hearts | 7 of Hearts | 8 of Hearts "
              "| 9 of Hearts | 10 of Hearts | Jack of Hearts | Queen of Hearts | King of Hearts | "
              "Ace of Spades | 2 of Spades | 3 of Spades | 4 of Spades | 5 of Spades | 6 of Spades | "
              "7 of Spades | 8 of Spades | 9 of Spades | 10 of Spades | Jack of Spades | "
              "Queen of Spades | King of Spades")
        self.assertEqual(d1.deck_as_text(),s, "Standard deck doesn't print correctly")
        self.assertEqual(d1.deck_as_text(verbose=True),sv, "Standard deck doesn't verbose print correctly")


    #test basic deck comparison
    def test_deck_comparison(self):
        d1 = cards.Deck()
        d2 = cards.Deck()
        self.assertEqual(d1, d2, "Deck comparison operator fails on 2 standard decks")

    #testing shuffled deck
    def test_shuffle_full_deck(self):
        d1 = cards.Deck()
        d2 = cards.Deck()
        d2.shuffle_deck()
        self.assertNotEqual(d1, d2, "Shuffled deck did not change") #might not be the perfect test case,
        #but statistically nearly impossible to shuffle deck back order
    
    #tests builtin python sort
    def test_shuffle_then_order_buildinsort_full_deck(self):
        d1 = cards.Deck()
        d2 = cards.Deck()
        d2.shuffle_deck()
        d2.order_deck()
        self.assertEqual(d1, d2, "Shuffled deck did not reorder on order() call")

    #tests self implemented quicksort
    def test_shuffle_then_order_mysort_full_deck(self):
        d1 = cards.Deck()
        d2 = cards.Deck()
        d2.shuffle_deck()
        d2.quick_sort_deck()
        self.assertEqual(d1, d2, "Shuffled deck did not reorder on order() call")

    #tests get suit method
    def test_get_suit_from_std_deck(self):
        d1 = cards.Deck()
        diamond_string = "AD | 2D | 3D | 4D | 5D | 6D | 7D | 8D | 9D | 10D | JD | QD | KD"
        club_string = "AC | 2C | 3C | 4C | 5C | 6C | 7C | 8C | 9C | 10C | JC | QC | KC"
        heart_string = "AH | 2H | 3H | 4H | 5H | 6H | 7H | 8H | 9H | 10H | JH | QH | KH"
        spade_string = "AS | 2S | 3S | 4S | 5S | 6S | 7S | 8S | 9S | 10S | JS | QS | KS"
        diamond_deck = d1.get_suit("Diamond")
        club_deck = d1.get_suit("Club")
        heart_deck = d1.get_suit("Heart")
        spade_deck = d1.get_suit("Spade")
        self.assertEqual(diamond_deck.deck_as_text(),diamond_string, "get_suit() failed Diamond")
        self.assertEqual(club_deck.deck_as_text(),club_string, "get_suit() failed Club")
        self.assertEqual(heart_deck.deck_as_text(),heart_string, "get_suit() failed Heart")
        self.assertEqual(spade_deck.deck_as_text(),spade_string, "get_suit() failed Spade")

    #tests get suit method on shuffled deck by counting suits
    def test_get_suit_from_shuffled_deck(self):
        d1 = cards.Deck()
        d1.shuffle_deck() #won't know the order due to shuffling so just count 13 diamonds
        diamond_deck = d1.get_suit("Diamond")
        self.assertEqual(13, diamond_deck.deck_as_text().count('D'), "get_suit() on shuffled failed Diamond")
        self.assertEqual(0, diamond_deck.deck_as_text().count('C'), "get_suit() on shuffled failed Diamond")
        self.assertEqual(0, diamond_deck.deck_as_text().count('H'), "get_suit() on shuffled failed Diamond")
        self.assertEqual(0, diamond_deck.deck_as_text().count('S'), "get_suit() on shuffled failed Diamond")

if __name__ == '__main__':
    unittest.main()