#
# Copyright 2017 Russell Smiley
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import unittest

import registerMap.utility.io.yaml.parameters.parse as rmpp
from registerMap.tests.expectedActual import simpleComparison


class TestBooleanParameter( unittest.TestCase ) :
    def testGoodData( self ) :
        def recordResult( value ) :
            nonlocal actualValue
            actualValue = value


        keyName = 'name'
        expectedValue = True
        yamlData = { keyName : expectedValue }

        actualValue = None
        goodResult = rmpp.booleanParameter( yamlData, keyName, recordResult )

        self.assertTrue( goodResult )
        self.assertEqual( actualValue, expectedValue )


class TestStringParameter( unittest.TestCase ) :
    def testGoodData( self ) :
        def recordResult( value ) :
            nonlocal actualValue
            actualValue = value


        keyName = 'name'
        expectedValue = 'value'

        yamlData = { keyName : expectedValue }

        actualValue = None
        goodResult = rmpp.stringParameter( yamlData, keyName, recordResult )

        simpleComparison( self, goodResult, True, 'good result' )
        simpleComparison( self, actualValue, expectedValue, 'parameter value' )


    def testBadKey( self ) :
        def recordResult( value ) :
            nonlocal actualValue
            actualValue = value


        keyName = 'name'
        expectedValue = 'value'

        yamlData = { keyName : expectedValue }

        actualValue = None
        with self.assertRaises( rmpp.ParseError ) :
            goodResult = rmpp.stringParameter( yamlData, 'parameter', recordResult )


class TestIntegerParameter( unittest.TestCase ) :
    def testGoodData( self ) :
        def recordResult( value ) :
            nonlocal actualValue
            actualValue = value


        keyName = 'offset'
        expectedValue = 10

        yamlData = { keyName : expectedValue }

        actualValue = None
        goodResult = rmpp.integerParameter( yamlData, keyName, recordResult )

        simpleComparison( self, goodResult, True, 'good result' )
        simpleComparison( self, actualValue, expectedValue, 'parameter value' )


    def testBadValue( self ) :
        def recordResult( value ) :
            nonlocal actualValue
            actualValue = value


        keyName = 'offset'
        expectedValue = 'value'

        yamlData = { keyName : expectedValue }

        actualValue = None
        goodResult = rmpp.integerParameter( yamlData, keyName, recordResult )

        simpleComparison( self, goodResult, False, 'good result' )
        simpleComparison( self, actualValue, None, 'parameter value' )


    def testNoneValueValid( self ) :
        def recordResult( value ) :
            nonlocal actualValue
            actualValue = value


        keyName = 'offset'
        expectedValue = None

        yamlData = { keyName : expectedValue }

        actualValue = None
        goodResult = rmpp.integerParameter( yamlData, keyName, recordResult,
                                            noneValid = True )

        simpleComparison( self, goodResult, True, 'good result' )
        simpleComparison( self, actualValue, None, 'parameter value' )


    def testNoneValueInvalid( self ) :
        def recordResult( value ) :
            nonlocal actualValue
            actualValue = value


        keyName = 'offset'
        expectedValue = None

        yamlData = { keyName : expectedValue }

        actualValue = None
        goodResult = rmpp.integerParameter( yamlData, keyName, recordResult )

        simpleComparison( self, goodResult, False, 'good result' )
        simpleComparison( self, actualValue, None, 'parameter value' )


    def testUseNameActive( self ) :
        def recordResult( name, value ) :
            nonlocal actualName, actualValue
            actualName = name
            actualValue = value


        keyName = 'offset'
        expectedValue = 3

        yamlData = { keyName : expectedValue }

        actualName = None
        actualValue = None
        goodResult = rmpp.integerParameter( yamlData, keyName, recordResult,
                                            useName = True )

        simpleComparison( self, goodResult, True, 'good result' )
        simpleComparison( self, actualName, keyName, 'parameter name' )
        simpleComparison( self, actualValue, expectedValue, 'parameter value' )


class TestComplexParameter( unittest.TestCase ) :
    def testGoodData( self ) :
        def doParseAction( thisData ) :
            nonlocal actualData

            thisGoodResult = True
            actualData = [ ]
            for element in thisData :
                try :
                    value = element[ 'name' ]
                    actualData.append( value )
                except KeyError :
                    thisGoodResult = False

            return thisGoodResult


        keyName = 'fields'

        yamlData = { keyName : [ { 'name' : 'one' }, { 'name' : 'two' }, { 'name' : 'three' } ] }

        actualData = None
        goodResult = rmpp.complexParameter( yamlData, keyName, doParseAction )

        simpleComparison( self, goodResult, True, 'good result' )
        simpleComparison( self, actualData, [ 'one', 'two', 'three' ], 'parameter value' )


    def testBadValue( self ) :
        def doParseAction( thisData ) :
            nonlocal actualData

            thisGoodResult = False

            return thisGoodResult


        keyName = 'fields'

        yamlData = { 'badName' : [ { 'name' : 'one' }, { 'name' : 'two' }, { 'name' : 'three' } ] }

        actualData = None
        with self.assertRaises( rmpp.ParseError ) :
            goodResult = rmpp.complexParameter( yamlData, keyName, doParseAction )


if __name__ == '__main__' :
    unittest.main( )
