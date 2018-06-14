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

import logging

from registerMap.exceptions import ParseError


log = logging.getLogger( __name__ )


def booleanParameter( yamlData, keyName, recordValue,
                      optional = False ) :
    value = None

    goodResult = True
    if keyName in yamlData :
        value = bool( yamlData[ keyName ] )
        recordValue( value )
    elif optional :
        log.debug( 'Yaml data does not specify an optional ' + keyName )
        goodResult = False
    else :
        raise ParseError( 'Yaml data does not specify a ' + keyName + '. ' + repr( yamlData ) )

    return goodResult


def stringParameter( yamlData, keyName, recordValue,
                     optional = False ) :
    value = None

    goodResult = True
    if keyName in yamlData :
        value = str( yamlData[ keyName ] )
        recordValue( value )
    elif optional :
        log.debug( 'Yaml data does not specify an optional ' + keyName )
        goodResult = False
    else :
        raise ParseError( 'Yaml data does not specify a ' + keyName + '. ' + repr( yamlData ) )

    return goodResult


def integerParameter( yamlData, keyName, recordValue,
                      optional = False,
                      noneValid = False,
                      useName = False ) :
    """
    Parse yaml data for an integer value.

    :param yamlData: Source yaml data.
    :param keyName: Parameter name.
    :param recordValue: Function to record the parameter value.
    :param optional: The parameter is optional, so no error state if parameter is not present.
    :param noneValid: The parameter value can be None.

    :return: Error state of parameter parsing.
    """
    value = None

    goodResult = True
    if keyName in yamlData :
        try :
            value = int( yamlData[ keyName ] )
            if useName :
                recordValue( keyName, value )
            else :
                recordValue( value )
        except ValueError :
            log.error( 'Yaml parameter ' + keyName + ' must be an integer. ' + repr( yamlData ) )
            goodResult = False
        except TypeError as e :
            if 'NoneType' not in str( e ) :
                log.error( 'Yaml parameer ' + keyName + ' must be an integer. ' + repr( yamlData ) )
                goodResult = False
            elif not noneValid :
                # Report an error for None value.
                log.error( 'Yaml parameer ' + keyName + ' must be an integer. ' + repr( yamlData ) )
                goodResult = False
    elif optional :
        log.debug( ' Yaml data does not specify an optional ' + keyName )
    else :
        log.error( 'Yaml data does not specify a ' + keyName + '. ' + repr( yamlData ) )
        goodResult = False

    return goodResult


def complexParameter( yamlData, keyName, doParsingAction,
                      optional = False ) :
    goodResult = True
    if keyName in yamlData :
        goodResult = doParsingAction( yamlData[ keyName ] )

        if not goodResult :
            raise ParseError( 'Incorrectly specified ' + keyName + '. ' + repr( yamlData ) )
    elif optional :
        log.debug( 'Yaml data does not specify an optional ' + keyName )
        goodResult = False
    else :
        raise ParseError( 'Yaml data does not specify ' + keyName + '.' + repr( yamlData ) )

    return goodResult
