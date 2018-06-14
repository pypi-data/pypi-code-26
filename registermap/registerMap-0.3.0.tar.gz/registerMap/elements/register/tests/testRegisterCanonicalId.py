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
from registerMap.set.fieldSet import FieldSet
from registerMap.structure.memory.space import MemorySpace

from ..register import Register


class TestRegisterCanonicalId( unittest.TestCase ) :
    def setUp( self ) :
        self.fieldSet = FieldSet()
        self.memorySpace = MemorySpace()


    def testGlobalCanonicalId( self ) :
        registerName = 'someName'

        testRegister = Register( self.memorySpace, self.fieldSet )
        testRegister[ 'name' ] = registerName

        expectedCanonicalId = '{0}'.format( registerName )

        self.assertEqual( testRegister.canonicalId, expectedCanonicalId )
        self.assertTrue( testRegister[ 'global' ] )


    def testLocalCanonicalId( self ) :
        moduleName = 'moduleName'
        registerName = 'someName'

        parentModule = Module( self.memorySpace, self.fieldSet )
        parentModule[ 'name' ] = moduleName

        testRegister = Register( self.memorySpace, self.fieldSet,
                                 parent = parentModule )
        testRegister[ 'name' ] = registerName

        expectedCanonicalId = '{0}.{1}'.format( moduleName,
                                                registerName )

        self.assertEqual( testRegister.canonicalId, expectedCanonicalId )
        self.assertFalse( testRegister[ 'global' ] )


if __name__ == '__main__' :
    unittest.main()
