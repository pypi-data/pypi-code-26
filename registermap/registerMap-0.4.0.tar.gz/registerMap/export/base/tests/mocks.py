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

from ..field import FieldBase
from ..memory import MemoryBase
from ..module import ModuleBase
from ..register import RegisterBase


class MockField( FieldBase ) :

    def __init__( self, fieldElement ) :
        super().__init__( fieldElement )

        self.expectedType = 'something'


    @property
    def type( self ) :
        return self.expectedType


class MockRegister( RegisterBase ) :

    def __init__( self, registerElement, FieldType ) :
        super().__init__( registerElement, FieldType )

        self.expectedAddress = '0x2f0d'
        self.expectedOffset = '0xf0d'


    @property
    def address( self ) :
        return self.expectedAddress


    @property
    def offset( self ) :
        return self.expectedOffset


class MockModule( ModuleBase ) :

    def __init__( self, moduleElement, RegisterType, FieldType ) :
        super().__init__( moduleElement, RegisterType, FieldType )

        self.expectedAddress = '0x20f0'
        self.expectedOffset = '0xf0'


    @property
    def address( self ) :
        return self.expectedAddress


    @property
    def offset( self ) :
        return self.expectedOffset


class MockMemory( MemoryBase ) :

    def __init__( self, memoryElement, memorySize ) :
        super().__init__( memoryElement, memorySize )


    @property
    def sizeType( self ) :
        return 'someValue'
