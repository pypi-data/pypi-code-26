# -*- coding: utf-8 -*-
"""
Created on Mon Jun  4 15:28:08 2018

@author: imarshal
"""
import random
suits = { "Diamond" : 0, "Club" : 1, "Heart" : 2 , "Spade" : 3 }
suit_names = ["Diamond", "Club", "Heart", "Spade"]

class Card():
    def __init__(self, value0, suit0):
        if (suit0 in suit_names and value0 in range(1, 14)):
            self.suit = suit0
            self.value = value0
            self.order = suits[suit0]*13+value0
        else:
            1 == 1
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
        ###default initializes in order deck
        self.cards = []
        if std_deck:
            for s in suit_names:
                for v in range(1, 14):
                    self.cards.append(Card(v, s))
    
    def __eq__(self, other):
        return (self.cards) == other.cards  

    def deck_as_text(self):
        deck_string = ''
        for c in self.cards:
            deck_string = deck_string + str(c.value) + c.suit[0] + " | "
        return deck_string[:-3]
    
    def shuffle_deck(self):
        random.shuffle(self.cards)
    
    def order_deck(self): #python 
        (self.cards).sort()

    def get_suit(self, suit0):
        d0 = Deck(std_deck=False)
        for c in self.cards:
            if c.suit == suit0:
                d0.cards.append(c)
        return d0
            
    def quick_sort_deck(self):
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
       


        
# if __name__ == '__main__':
#     print suits
#     print suits.keys()
#     print suits.items()
    #c1 = Card(3, "Heart")
    #c1.print()
    #c1.verbose_print()
    # print("============Initialize Deck============")
    # d1 = Deck()
    # h1 = d1.get_suit("Spades")
    # print(d1.deck_as_text())
    # print("============Initialize Deck============")
    # pritn(h1.deck_as_text())
    # print("=============Shuffled===============")
    # d1.shuffle_deck()
    # h1 = d1.get_suit("Spades")
    # print(d1.deck_as_text())
    # print("==============Re ordered===============")
    # d1.order_deck()
    # print(d1.deck_as_text())
    # print("=============Shuffled Again===============")
    # d1.shuffle_deck()
    # print(d1.deck_as_text())
    # print("=============Quick Sort===============")
    # d1.quick_sort_deck()
    # print(d1.deck_as_text())