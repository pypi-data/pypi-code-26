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
from registerMap.set import SetCollection
from registerMap.structure.memory.space import MemorySpace

from ..parameters import ElementsParameter


class TestElementsParameter( unittest.TestCase ) :
    def setUp( self ) :
        def setupSetCollection() :
            m = self.createModule( 'module' )

            r = m.addRegister( 'register' )

            lf = r.addField( 'local-field', [ 0, 3 ] )

            self.assertEqual( 'module.register.local-field', lf.canonicalId )

            gf = r.addField( 'global-field', [ 5, 6 ],
                             isGlobal = True )
            self.assertEqual( 'global-field', gf.canonicalId )


        self.memorySpace = MemorySpace()
        self.setCollection = SetCollection()

        setupSetCollection()

        self.testElements = ElementsParameter( self.setCollection )


    def createModule( self, name ) :
        thisModule = Module( self.memorySpace, self.setCollection )
        thisModule[ 'name' ] = name

        self.setCollection.moduleSet.add( thisModule )

        return thisModule


    def testGlobalFieldFound( self ) :
        actualElement = self.testElements[ 'global-field' ]

        self.assertIsNotNone( actualElement )
        self.assertEqual( actualElement[ 'name' ], 'global-field' )


    def testLocalFieldFound( self ) :
        actualElement = self.testElements[ 'module.register.local-field' ]

        self.assertIsNotNone( actualElement )
        self.assertEqual( actualElement[ 'name' ], 'local-field' )


    def testRegisterFound( self ) :
        actualElement = self.testElements[ 'module.register' ]

        self.assertIsNotNone( actualElement )
        self.assertEqual( actualElement[ 'name' ], 'register' )


    def testModuleFound( self ) :
        actualElement = self.testElements[ 'module' ]

        self.assertIsNotNone( actualElement )
        self.assertEqual( actualElement[ 'name' ], 'module' )


    def testElementNotFound( self ) :
        actualElement = self.testElements[ 'not-an-element' ]

        self.assertIsNone( actualElement )


if __name__ == '__main__' :
    unittest.main()
