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
from rama.framework import Attribute, Composition, Reference, BaseType
from rama.models.ivoa import StringQuantity
from rama.models.measurements import CoordMeasure
from rama.utils.registry import VO


@VO('source:LuminosityType')
class LuminosityType(StringQuantity):
    pass


@VO('source:LuminosityType1')
class LuminosityType1(StringQuantity):
    pass


@VO('source:LuminosityType2')
class LuminosityType2(StringQuantity):
    pass


@VO('source:Algorithm')
class Algorithm(BaseType):
    description = Attribute('source:Algorithm.description', min_occurs=0, max_occurs=1)


@VO('source:Catalogue')
class Catalogue(BaseType):
    source = Composition('source:Catalogue.source', min_occurs=0, max_occurs=-1)


@VO('source:Source')
class Source(BaseType):
    name = Attribute('source:Source.name', min_occurs=0, max_occurs=1)
    classification = Attribute('source:Source.classification', min_occurs=0, max_occurs=1)
    luminosity = Composition('source:Source.luminosity', min_occurs=0, max_occurs=-1)
    position = Composition('source:Source.position', min_occurs=1, max_occurs=-1)


@VO('source:Detection')
class Detection(Source):
    source_image = Composition('source:Detection.sourceImage', min_occurs=1, max_occurs=-1)


@VO('source:Image')
class Image(BaseType):
    url = Attribute('source:Image.url', min_occurs=0, max_occurs=1)
    exposure_time = Attribute('source:Image.exposureTime', min_occurs=0, max_occurs=1)
    start_time = Attribute('source:Image.startTime', min_occurs=0, max_occurs=1)
    end_time = Attribute('source:Image.endTime', min_occurs=0, max_occurs=1)
    filter = Reference('source:Image.filter', min_occurs=1, max_occurs=1)


@VO('source:LuminosityMeasurement')
class LuminosityMeasurement(BaseType):
    value = Attribute('source:LuminosityMeasurement.value', min_occurs=1, max_occurs=1)
    error = Attribute('source:LuminosityMeasurement.error', min_occurs=1, max_occurs=1)
    type = Attribute('source:LuminosityMeasurement.type', min_occurs=1, max_occurs=1)
    filter = Reference('source:LuminosityMeasurement.filter', min_occurs=1, max_occurs=1)
    algorithm = Reference('source:LuminosityMeasurement.algorithm', min_occurs=0, max_occurs=1)


@VO('source:SourceImage')
class SourceImage(BaseType):
    image = Reference('source:SourceImage.image', min_occurs=1, max_occurs=1)


@VO('source:SourcePosition')
class SourcePosition(CoordMeasure):
    algorithm = Reference('source:SourcePosition.algorithm', min_occurs=1, max_occurs=1)


@VO('source:XMatchSource')
class XMatchSource(BaseType):
    weight = Attribute('source:XMatchSource.weight', min_occurs=0, max_occurs=1)
    source = Reference('source:XMatchSource.source', min_occurs=1, max_occurs=1)


@VO('source:XMatchTuple')
class XMatchTuple(Source):
    source = Composition('source:XMatchTuple.source', min_occurs=1, max_occurs=-1)
