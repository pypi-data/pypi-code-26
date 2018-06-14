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

import unittest

from registerMap.structure.memory.space import MemorySpace
from registerMap.set import SetCollection


class CommonFieldIntervalTests :
    class TestRegisterDefaultFieldInterval( unittest.TestCase ) :
        # The tests will fail unless a test case loader correctly fulfills this value.
        RegisterType = None


        def setUp( self ) :
            self.setCollection = SetCollection()
            self.memorySpace = MemorySpace()

            self.registerUnderTest = self.RegisterType( self.memorySpace,
                                                        setCollection = self.setCollection )


        def testDefaultFieldInterval( self ) :
            # When creating a new field, only specifying the register interval assume the field is the size of the register.
            self.assertEqual( len( self.setCollection.fieldSet ), 0 )

            self.registerUnderTest.addField( 'newField', [ 5, 8 ] )

            newFields = self.setCollection.fieldSet.find( 'newField' )
            self.assertEqual( len( newFields ), 1 )

            newField = newFields.pop()
            self.assertEqual( newField.sizeBits, 4 )


        def testMissingFieldIntervalAsserts( self ) :
            # Not specifying the field interval when changing an existing field asserts

            self.registerUnderTest.addField( 'newField', [ 5, 8 ] )
            self.assertEqual( len( self.setCollection.fieldSet ), 1 )

            with self.assertRaises( AssertionError ) :
                self.registerUnderTest.addField( 'newField', [ 9, 10 ] )
