# Copyright 2018 Smithsonian Astrophysical Observatory
#
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
# following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following
# disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following
# disclaimer in the documentation and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote
# products derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
from rama.models.measurements import Measure

from rama.adapters.cube import CubePoint
from rama.framework import Composition, Attribute, Reference, BaseType
from rama.utils import Adapter
from rama.utils.registry import VO


@VO('cube:DataProduct')
class DataProduct(BaseType):
    coord_sys = Composition('cube:DataProduct.coordSys', min_occurs=1, max_occurs=-1)
    mappings = Composition('cube:DataProduct.mappings', min_occurs=0, max_occurs=1)
    dataset = Reference('cube:DataProduct.dataset', min_occurs=1, max_occurs=1)


@VO('cube:NDImage')
class NDImage(DataProduct):
    data = Composition('cube:NDImage.data', min_occurs=0, max_occurs=-1)
    pixel_coord_sys = Composition('cube:NDImage.pixelCoordSys', min_occurs=1, max_occurs=1)


@VO('cube:SparseCube')
class SparseCube(DataProduct):
    data = Composition('cube:SparseCube.data', min_occurs=0, max_occurs=-1)


@VO('cube:Voxel')
class Voxel(BaseType):
    pixel_axis = Composition('cube:Voxel.pixelAxis', min_occurs=1, max_occurs=-1)
    value_axis = Composition('cube:Voxel.valueAxis', min_occurs=1, max_occurs=1)
    coord_axis = Composition('cube:Voxel.coordAxis', min_occurs=0, max_occurs=-1)


@VO('cube:NDPoint')
@Adapter(CubePoint)
class NDPoint(BaseType):
    observable = Composition('cube:NDPoint.observable', min_occurs=0, max_occurs=-1)


@VO('cube:DataAxis')
class DataAxis(BaseType):
    dependent = Attribute('cube:DataAxis.dependent', min_occurs=1, max_occurs=1)


@VO('cube:ImageAxis')
class ImageAxis(DataAxis):
    pass


@VO('cube:PixelAxis')
class PixelAxis(ImageAxis):
    coord = Attribute('cube:PixelAxis.coord', min_occurs=1, max_occurs=1)


@VO('cube:MeasurementAxis')
class MeasurementAxis(DataAxis):
    measure = Composition('cube:MeasurementAxis.measure', min_occurs=1, max_occurs=1)


@VO('cube:Observable')
class Observable(MeasurementAxis):
    pass


@VO('cube:ValueAxis')
class ValueAxis(MeasurementAxis):
    pass


@VO('cube:VirtualMeasure')
class VirtualMeasure(Measure):
    result_type = Attribute('cube:VirtualMeasure.result_type', min_occurs=1, max_occurs=1)
    source = Reference('cube:VirtualMeasure.source', min_occurs=1, max_occurs=-1)
    transform = Reference('cube:VirtualMeasure.transform', min_occurs=0, max_occurs=1)
    result_frame = Reference('cube:VirtualMeasure.result_frame', min_occurs=0, max_occurs=1)


@VO('cube:VirtualImageAxis')
class VirtualImageAxis(ImageAxis):
    result_type = Attribute('cube:VirtualImageAxis.result_type', min_occurs=1, max_occurs=1)
    source = Reference('cube:VirtualImageAxis.source', min_occurs=1, max_occurs=-1)
    transform = Reference('cube:VirtualImageAxis.transform', min_occurs=0, max_occurs=1)
    result_frame = Reference('cube:VirtualImageAxis.result_frame', min_occurs=0, max_occurs=1)


@VO('cube:Transform')
class Transform(BaseType):
    pass
