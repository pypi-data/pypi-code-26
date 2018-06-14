#
# Copyright 2017 Russell Smiley
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

from registerMap.elements.module import Module
from registerMap.elements.register import RegisterInstance
from registerMap.set.fieldSet import FieldSet
from registerMap.structure.memory.space import MemorySpace

from .. import Field


class TestFieldCanonicalId( unittest.TestCase ) :
    def setUp( self ) :
        self.fieldSet = FieldSet()
        self.memorySpace = MemorySpace()


    def testGlobalCanonicalId( self ) :
        fieldName = 'thisField'

        testField = Field()
        testField[ 'name' ] = fieldName

        expectedCanonicalId = '{0}'.format( fieldName )

        self.assertEqual( testField.canonicalId, expectedCanonicalId )
        self.assertTrue( testField[ 'global' ] )


    def testLocalCanonicalId( self ) :
        fieldName = 'thisField'
        moduleName = 'thisModule'
        registerName = 'thisRegister'

        parentModule = Module( self.memorySpace, self.fieldSet )
        parentModule[ 'name' ] = moduleName

        parentRegister = RegisterInstance( self.memorySpace,
                                           parent = parentModule,
                                           setCollection = self.fieldSet )
        parentRegister[ 'name' ] = registerName

        testField = Field( parent = parentRegister )
        testField[ 'name' ] = fieldName

        expectedCanonicalId = '{0}.{1}.{2}'.format( moduleName,
                                                    registerName,
                                                    fieldName )

        self.assertEqual( testField.canonicalId, expectedCanonicalId )
        self.assertFalse( testField[ 'global' ] )


if __name__ == '__main__' :
    unittest.main()
