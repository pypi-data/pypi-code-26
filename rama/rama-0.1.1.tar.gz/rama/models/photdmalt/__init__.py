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
from rama.utils.registry import VO


@VO('photdm-alt:S_Bounds')
class S_Bounds:
    extent = Attribute('photdm-alt:S_Bounds.extent', min_occurs=0, max_occurs=1)
    start = Attribute('photdm-alt:S_Bounds.start', min_occurs=1, max_occurs=1)
    stop = Attribute('photdm-alt:S_Bounds.stop', min_occurs=1, max_occurs=1)


@VO('photdm-alt:Access')
class Access(BaseType):
    reference = Attribute('photdm-alt:Access.reference', min_occurs=1, max_occurs=1)
    format = Attribute('photdm-alt:Access.format', min_occurs=1, max_occurs=1)
    size = Attribute('photdm-alt:Access.size', min_occurs=0, max_occurs=1)


@VO('photdm-alt:ZeroPoint')
class ZeroPoint(BaseType):
    flux = Attribute('photdm-alt:ZeroPoint.flux', min_occurs=1, max_occurs=1)
    reference_magnitude = Attribute('photdm-alt:ZeroPoint.referenceMagnitude', min_occurs=1, max_occurs=1)


@VO('photdm-alt:AsinhZeroPoint')
class AsinhZeroPoint(ZeroPoint):
    softening_coefficient = Attribute('photdm-alt:AsinhZeroPoint.softeningCoefficient', min_occurs=0, max_occurs=1)


@VO('photdm-alt:LinearFlux')
class LinearFlux(ZeroPoint):
    pass


@VO('photdm-alt:MagnitudeSystem')
class MagnitudeSystem(BaseType):
    type = Attribute('photdm-alt:MagnitudeSystem.type', min_occurs=0, max_occurs=1)
    reference_spectrum = Attribute('photdm-alt:MagnitudeSystem.referenceSpectrum', min_occurs=0, max_occurs=1)
    source = Composition('photdm-alt:MagnitudeSystem.source', min_occurs=0, max_occurs=-1)


@VO('photdm-alt:PhotCal')
class PhotCal(BaseType):
    zero_point = Composition('photdm-alt:PhotCal.zeroPoint', min_occurs=1, max_occurs=1)
    magnitude_system = Composition('photdm-alt:PhotCal.magnitudeSystem', min_occurs=1, max_occurs=1)
    photometry_filter = Reference('photdm-alt:PhotCal.photometryFilter', min_occurs=1, max_occurs=1)


@VO('photdm-alt:PhotometricSystem')
class PhotometricSystem(BaseType):
    description = Attribute('photdm-alt:PhotometricSystem.description', min_occurs=0, max_occurs=1)
    detector_type = Attribute('photdm-alt:PhotometricSystem.detectorType', min_occurs=1, max_occurs=1)
    photometry_filter = Composition('photdm-alt:PhotometricSystem.photometryFilter', min_occurs=1, max_occurs=-1)


@VO('photdm-alt:PhotometryFilter')
class PhotometryFilter(BaseType):
    fps_identifier = Attribute('photdm-alt:PhotometryFilter.fpsIdentifier', min_occurs=1, max_occurs=1)
    identifier = Attribute('photdm-alt:PhotometryFilter.identifier', min_occurs=1, max_occurs=1)
    name = Attribute('photdm-alt:PhotometryFilter.name', min_occurs=1, max_occurs=1)
    description = Attribute('photdm-alt:PhotometryFilter.description', min_occurs=1, max_occurs=1)
    band_name = Attribute('photdm-alt:PhotometryFilter.bandName', min_occurs=1, max_occurs=1)
    data_validity_from = Attribute('photdm-alt:PhotometryFilter.dataValidityFrom', min_occurs=1, max_occurs=1)
    data_validity_to = Attribute('photdm-alt:PhotometryFilter.dataValidityTo', min_occurs=1, max_occurs=1)
    spectral_location = Attribute('photdm-alt:PhotometryFilter.spectralLocation', min_occurs=1, max_occurs=1)
    band_width = Attribute('photdm-alt:PhotometryFilter.bandWidth', min_occurs=1, max_occurs=1)
    transmission_point = Composition('photdm-alt:PhotometryFilter.transmissionPoint', min_occurs=0, max_occurs=-1)
    access = Composition('photdm-alt:PhotometryFilter.access', min_occurs=0, max_occurs=1)


@VO('photdm-alt:PogsonZeroPoint')
class PogsonZeroPoint(ZeroPoint):
    pass


@VO('photdm-alt:Source')
class Source(BaseType):
    pass


@VO('photdm-alt:TransmissionPoint')
class TransmissionPoint(BaseType):
    spectral = Attribute('photdm-alt:TransmissionPoint.spectral', min_occurs=1, max_occurs=1)
    spectral_error = Attribute('photdm-alt:TransmissionPoint.spectralError', min_occurs=1, max_occurs=1)
    transmission = Attribute('photdm-alt:TransmissionPoint.transmission', min_occurs=1, max_occurs=1)
    transmission_error = Attribute('photdm-alt:TransmissionPoint.transmissionError', min_occurs=1, max_occurs=1)
