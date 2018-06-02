# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Copyright 2018 SerialLab Corp.  All rights reserved.

from quartet_masterdata import models
from quartet_masterdata import serializers
from rest_framework.viewsets import ModelViewSet


class LocationViewSet(ModelViewSet):
    '''
    CRUD ready model view for the Location model.
    '''
    queryset = models.Location.objects.all()
    serializer_class = serializers.LocationSerializer


class LocationTypeViewSet(ModelViewSet):
    '''
    CRUD ready model view for the LocationType model.
    '''
    queryset = models.LocationType.objects.all()
    serializer_class = serializers.LocationTypeSerializer


class LocationIdentifierViewSet(ModelViewSet):
    '''
    CRUD ready model view for the LocationIdentifier model.
    '''
    queryset = models.LocationIdentifier.objects.all()
    serializer_class = serializers.LocationIdentifierSerializer


class LocationFieldViewSet(ModelViewSet):
    '''
    CRUD ready model view for the LocationField model.
    '''
    queryset = models.LocationField.objects.all()
    serializer_class = serializers.LocationFieldSerializer


class MeasurementViewSet(ModelViewSet):
    '''
    CRUD ready model view for the Measurement model.
    '''
    queryset = models.Measurement.objects.all()
    serializer_class = serializers.MeasurementSerializer


class TradeItemViewSet(ModelViewSet):
    '''
    CRUD ready model view for the TradeItem model.
    '''
    queryset = models.TradeItem.objects.all()
    serializer_class = serializers.TradeItemSerializer


class TradeItemFieldViewSet(ModelViewSet):
    '''
    CRUD ready model view for the TradeItemField model.
    '''
    queryset = models.TradeItemField.objects.all()
    serializer_class = serializers.TradeItemFieldSerializer
