#
# Copyright 2018 Russell Smiley
#
# This file is part of registerMap.
#
# registerMap is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# registerMap is distributed in the hope that it will be useful
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with registerMap.  If not, see <http://www.gnu.org/licenses/>.
#

import collections


class ElementList( collections.OrderedDict ) :
    """
    Manage the instances of addressable memory elements such as module and register.

    The list maintains the notification relationships between element regarding address and size changes.
    """
    def __init__( self, owner ) :
        """

        :param owner: RegisterMap or Module object who "owns" the list of sub elements.
        """
        super().__init__()
        self.__owner = owner


    def __setitem__( self, key, value ) :
        try :
            previousElementKey = next( reversed( self ) )
            previousElement = self[ previousElementKey ]
        except StopIteration as e :
            # This is the first register added.
            previousElement = self.__owner.firstElement

        super().__setitem__( key, value )

        # Link the value being added to it's previous element in the list.
        value.previousElement = previousElement

        # Size change of an element means the owner might also need to change size.
        value.sizeChangeNotifier.addObserver( self.__owner.sizeObserver )

        # Address change of an element implies a potential size change to its owner.
        value[ 'constraints' ].addressChangeNotifier.addObserver( self.__owner.sizeObserver )
        value.reviewAddressChange()
