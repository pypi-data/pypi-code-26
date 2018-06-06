import random
suits = { "Diamond" : 0, "Club" : 1, "Heart" : 2 , "Spade" : 3 }
suit_names = ["Diamond", "Club", "Heart", "Spade"]
values = ["Ace", "2", "3", "4" , "5", "6", "7", "8", "9", "10", "Jack", "Queen", "King"]

class Card():
    def __init__(self, value0, suit0):
        if (suit0 in suit_names and value0 in range(1, 14)):
            self.suit = suit0
            self.value = value0
            self.order = suits[suit0]*13+value0
        else:
            raise ValueError("Invalid Card")
            #invalid card
    #overload comaprison operators for easier sorting
    def __eq__(self, other):
        return (self.order) == other.order                     
    def __lt__(self, other):
        return (self.order) < other.order
    def __gt__(self, other):
        return (self.order) > other.order
    def __le__(self, other):
        return (self.order) <= other.order
    def __ge__(self, other):
        return (self.order) >= other.order


class Deck():
    def __init__(self, std_deck=True):
        """Deck constructor, default to a standard in order deck, 
           std_deck=False will return a Deck object with empty card list
           so a custom deck can be inserted by another method
        Parameters
        ----------
        verbose : bool
            False (default) - returns shortend card names in the form AD | 2D ... etc.
            True - returns longer names in the form in the form Ace of Diamonds | 2 of ...

        Returns
        -------
        str
            Returns 

        """ 
        self.cards = []
        if std_deck:
            for s in suit_names:
                for v in range(1, 14):
                    self.cards.append(Card(v, s))

    def __eq__(self, other):
        """Deck1 == Deck2 if card lists match order and size"""
        return self.cards == other.cards  

    def deck_as_text(self, verbose=False):
        """
        Creates string from deck object for viewing order of cards

        Parameters
        ----------
        verbose : bool
            False (default) - returns shortend card names in the form AD | 2D ... etc.
            True - returns longer names in the form in the form Ace of Diamonds | 2 of ...

        Returns
        -------
        str "|" delineated list of cards

        """ 
        deck_string = ''
        if not verbose:
            for c in self.cards:
                if c.value == 10:
                    deck_string = deck_string + values[c.value - 1] + c.suit[0] + " | " #10 is only 2 digit num
                else:
                    deck_string = deck_string + values[c.value - 1][0] + c.suit[0] + " | "
            return deck_string[:-3]
        else:
            for c in self.cards:
                deck_string = deck_string + values[c.value - 1] + " of " + c.suit + "s | "
            return deck_string[:-3]
    
    def shuffle_deck(self):
        """ Randomizes Deck order""" 
        random.shuffle(self.cards)
    
    def order_deck(self): 
        """ Sorts deck based based on standard order using pythons builtin sort """
        (self.cards).sort()

    def get_suit(self, suit0):
        """
        Creates string from deck object for viewing order of cards

        Parameters
        ----------
        verbose : bool
            False (default) - returns shortend card names in the form AD | 2D ... etc.
            True - returns longer names in the form in the form Ace of Diamonds | 2 of ...

        Returns
        -------
        str "|" delineated list of cards

        """ 
        if suit0 in suits:
            d0 = Deck(std_deck=False)
            for c in self.cards:
                if c.suit == suit0:
                    d0.cards.append(c)
            return d0
        else:
            raise ValueError("""Invalid Suit, Call get_suit() with ["Diamond", "Club", "Heart", "Spade"]""")
    def quick_sort_deck(self):
        """ Sorts deck based based on standard order using own sorting algorithm modeled after quick sort """   
        #Define Helpers so we can pass only the Deck
        def quick_sort_helper(card_list, first, last):
            if first<last:
               splitpoint = partition(card_list,first,last)
               quick_sort_helper(card_list,first,splitpoint-1)
               quick_sort_helper(card_list,splitpoint+1,last)
    
        def partition(card_list, first, last):
            pivotvalue = card_list[first]
            left = first+1
            right = last
            while True:
                while left <= right and card_list[left] <= pivotvalue:
                    left = left + 1
    
                while card_list[right] >= pivotvalue and right >= left:
                    right = right -1
                if right < left:
                    break #sub list sorted
                else:
                    temp = card_list[left]
                    card_list[left] = card_list[right]
                    card_list[right] = temp
            temp = card_list[first]
            card_list[first] = card_list[right]
            card_list[right] = temp
            return right       
        card_list = self.cards
        quick_sort_helper(card_list,0,len(card_list)-1)
        self.cards = card_list