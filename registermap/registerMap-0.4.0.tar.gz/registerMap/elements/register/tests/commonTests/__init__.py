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

import types

from .description import CommonDescriptionParameterTests
from .fieldInterval import CommonFieldIntervalTests
from .fields import CommonFieldTests
from .mode import CommonModeParameterTests
from .name import CommonNameParameterTests
from .public import CommonPublicParameterTests
from .sizeBits import CommonSizeBitsTests
from .summary import CommonSummaryParameterTests
from .userDefinedParameters import CommonUserDefinedParameterTests
from .yamlIo import CommonYamlIoTests


commonTests = [
    CommonDescriptionParameterTests.TestRegisterDescription,
    CommonFieldIntervalTests.TestRegisterDefaultFieldInterval,
    CommonFieldTests.TestRegisterFields,
    CommonFieldTests.TestFieldsMultipleRegisters,
    CommonModeParameterTests.TestRegisterMode,
    CommonNameParameterTests.TestRegisterName,
    CommonPublicParameterTests.TestRegisterPublic,
    CommonSizeBitsTests.TestRegisterSize,
    CommonSizeBitsTests.TestRegisterSizeBits,
    CommonSummaryParameterTests.TestRegisterSummary,
    CommonUserDefinedParameterTests.TestRegisterUserDefinedParameter,
    CommonYamlIoTests.TestRegisterYamlLoadSave,
    CommonYamlIoTests.TestRegisterYamlLoadSaveCanonicalId,
    CommonYamlIoTests.TestRegisterYamlParameters,
    CommonYamlIoTests.TestLoadSaveUserDefinedParameter,
]


def copyCommonClasses( typename ) :
    renamedTests = list()
    for thisTest in commonTests :
        newTest = type( '{0}_{1}'.format( typename, thisTest.__name__ ), thisTest.__bases__,
                        dict( thisTest.__dict__ ) )
        renamedTests.append( newTest )

    return renamedTests


def addCommonTestCases( UnderTestType, thisSuite ) :
    thisTests = copyCommonClasses( UnderTestType.__name__ )
    for thisTestCase in thisTests :
        thisTestCase.RegisterType = UnderTestType

        testMethods = [ x for x, y in thisTestCase.__dict__.items() if
                        (type( y ) == types.FunctionType) and x.startswith( 'test' ) ]

        for thisTest in testMethods :
            thisSuite.addTest( thisTestCase( thisTest ) )

    return thisSuite
