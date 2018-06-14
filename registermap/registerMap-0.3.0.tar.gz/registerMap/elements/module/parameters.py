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

from registerMap.exceptions import ParseError
from registerMap.utility.observer import \
    Observable, \
    SizeChangeObserver

from ..base import ElementList
from ..base.parameter import Parameter
from ..register import RegisterInstance


class RegistersParameter( Parameter ) :
    __parameterName = 'registers'


    class FirstRegister :
        def __init__( self,
                      endAddress = None ) :
            self.addressChangeNotifier = Observable()
            self.sizeChangeNotifier = Observable()

            self.__endAddress = endAddress


        @property
        def endAddress( self ) :
            return self.__endAddress


        @endAddress.setter
        def endAddress( self, value ) :
            self.__endAddress = value
            # Notify observers that their address might need to change.
            self.addressChangeNotifier.notifyObservers()


    def __init__( self, owner ) :
        super().__init__( self.__parameterName, ElementList( self ) )

        self.__owner = owner

        self.firstElement = None
        self.sizeObserver = SizeChangeObserver( self.__owner )

        self.__createFirstRegisterPrevious()


    def __createFirstRegisterPrevious( self ) :
        if self.__owner.baseAddress is None :
            # Have to deal with None addresses as a special case
            thisEndAddress = None
        else :
            thisEndAddress = (self.__owner.baseAddress - 1)

        self.firstElement = RegistersParameter.FirstRegister( endAddress = thisEndAddress )


    @classmethod
    def from_yamlData( cls, yamlData, owner, memorySpace, setCollection,
                       optional = False,
                       parent = None ) :
        parameter = cls( owner )
        if (not optional) and (cls.__parameterName not in yamlData.keys()) :
            raise ParseError( 'Registers not defined in yaml data' )
        elif cls.__parameterName in yamlData.keys() :
            for registerYamlData in yamlData[ cls.__parameterName ] :
                register = RegisterInstance.from_yamlData( registerYamlData, memorySpace, setCollection,
                                                           parent = parent )
                parameter.value[ register[ 'name' ] ] = register

        return parameter


    def to_yamlData( self ) :
        yamlData = { self.__parameterName : list() }

        for register in self.value.values() :
            yamlData[ self.__parameterName ].append( register.to_yamlData() )

        return yamlData
