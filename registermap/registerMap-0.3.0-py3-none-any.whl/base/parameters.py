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


from ..elements.base import ElementList
from ..elements.module import Module
from ..elements.base.parameter import Parameter
from ..exceptions import ParseError

from ..utility.observer import \
    Observable, \
    SizeChangeObserver


class ElementsParameter( Parameter ) :
    def __init__( self, setCollection ) :
        self.__setCollection = setCollection


    def __getitem__( self, item ) :
        fields = [ x for x in self.__setCollection.fieldSet if x.canonicalId == item ]
        if len( fields ) == 0 :
            registers = [ x for x in self.__setCollection.registerSet if x.canonicalId == item ]

            if len( registers ) == 0 :
                modules = [ x for x in self.__setCollection.moduleSet if x.canonicalId == item ]

                if len( modules ) == 0 :
                    foundItem = None
                else :
                    assert len( modules ) == 1

                    foundItem = modules[ 0 ]
            else :
                assert len( registers ) == 1

                foundItem = registers[ 0 ]

        else :
            # Canonical ID is supposed to be unique so there should be only one result.
            assert len( fields ) == 1

            foundItem = fields[ 0 ]

        return foundItem

    def to_yamlData( self ) :
        # ElementParameter should not be stored in YAML. It should be built in situ when acquired from YAML.
        return None


class ModulesParameter( Parameter ) :
    __parameterName = 'modules'


    class FirstModule :
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
            self.sizeChangeNotifier.notifyObservers()


    def __init__( self, owner ) :
        super().__init__( self.__parameterName, ElementList( self ) )

        self.__owner = owner

        self.firstElement = None
        self.sizeObserver = SizeChangeObserver( self.__owner )

        self.__createFirstModulePrevious()


    def __createFirstModulePrevious( self ) :
        assert self.__owner.memory.baseAddress >= 0
        firstModule = ModulesParameter.FirstModule( endAddress = (self.__owner.memory.baseAddress - 1) )

        self.firstElement = firstModule


    @classmethod
    def from_yamlData( cls, yamlData, owner, memorySpace, bitFieldSet,
                       optional = False ) :
        parameter = cls( owner )
        if (not optional) and (cls.__parameterName not in yamlData.keys()) :
            raise ParseError( 'Modules not defined in yaml data' )
        elif cls.__parameterName in yamlData.keys() :
            for moduleYamlData in yamlData[ cls.__parameterName ] :
                module = Module.from_yamlData( moduleYamlData, memorySpace, bitFieldSet )
                parameter.value[ module[ 'name' ] ] = module

        return parameter


    def to_yamlData( self ) :
        yamlData = { self.__parameterName : list() }

        for register in self.value.values() :
            yamlData[ self.__parameterName ].append( register.to_yamlData() )

        return yamlData
