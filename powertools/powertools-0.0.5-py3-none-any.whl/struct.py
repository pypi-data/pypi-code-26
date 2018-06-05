#-- powertools.struct

"""
data structures
"""

# import sys
# from pprint import pprint
# import traceback

#----------------------------------------------------------------------------------------------#


from ordered_set import OrderedSet
class GreedyOrderedSet( OrderedSet ) :
    '''OrderedSet that keeps the last value added to it instead of the first.'''

    def add( self, key ) :
        """ Add `key` as an item to this OrderedSet, then return its index.
            If `key` is already in the OrderedSet, delete it and add it again.
        """

        if key not in self.map :
            self.map[key] = len( self.items )
            self.items.append( key )
        else :
            self.discard( key )
            self.add( key )
        return self.map[key]

    append = add


#----------------------------------------------------------------------------------------------#
