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

import registerMap.set.fieldSet as rmsfs
import registerMap.structure.memory.space as rmm

from .. import Module


class TestModuleCananicalId( unittest.TestCase ) :
    def setUp( self ) :
        self.fieldSet = rmsfs.FieldSet()
        self.memorySpace = rmm.MemorySpace()

        self.testModule = Module( self.memorySpace, self.fieldSet )


    def testCanonicalIdOkay( self ) :
        expectedName = 'someName'

        self.testModule[ 'name' ] = expectedName

        self.assertEqual( self.testModule.canonicalId, expectedName )


if __name__ == '__main__' :
    unittest.main()
