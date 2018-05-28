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
from rama.framework import Attribute, Composition, BaseType
from rama.utils.registry import VO


@VO('meas:Uncertainty')
class Uncertainty(BaseType):
    pass


@VO('meas:Uncertainty1D')
class Uncertainty1D(Uncertainty):
    pass


@VO('meas:Uncertainty2D')
class Uncertainty2D(Uncertainty):
    pass


@VO('meas:Uncertainty3D')
class Uncertainty3D(Uncertainty):
    pass


@VO('meas:Symmetrical1D')
class Symmetrical1D(Uncertainty1D):
    radius = Attribute('meas:Symmetrical1D.radius', min_occurs=1, max_occurs=1)


@VO('meas:Asymmetrical1D')
class Asymmetrical1D(Uncertainty1D):
    plus = Attribute('meas:Asymmetrical1D.plus', min_occurs=1, max_occurs=1)
    minus = Attribute('meas:Asymmetrical1D.minus', min_occurs=1, max_occurs=1)


@VO('meas:Bounds1D')
class Bounds1D(Uncertainty1D):
    lo_limit = Attribute('meas:Bounds1D.loLimit', min_occurs=1, max_occurs=1)
    hi_limit = Attribute('meas:Bounds1D.hiLimit', min_occurs=1, max_occurs=1)


@VO('meas:Symmetrical2D')
class Symmetrical2D(Uncertainty2D):
    radius = Attribute('meas:Symmetrical2D.radius', min_occurs=1, max_occurs=1)


@VO('meas:Asymmetrical2D')
class Asymmetrical2D(Uncertainty2D):
    plus = Attribute('meas:Asymmetrical2D.plus', min_occurs=2, max_occurs=2)
    minus = Attribute('meas:Asymmetrical2D.minus', min_occurs=2, max_occurs=2)


@VO('meas:Bounds2D')
class Bounds2D(Uncertainty2D):
    lo_limit = Attribute('meas:Bounds2D.loLimit', min_occurs=2, max_occurs=2)
    hi_limit = Attribute('meas:Bounds2D.hiLimit', min_occurs=2, max_occurs=2)


@VO('meas:Symmetrical3D')
class Symmetrical3D(Uncertainty3D):
    radius = Attribute('meas:Symmetrical3D.radius', min_occurs=1, max_occurs=1)


@VO('meas:Asymmetrical3D')
class Asymmetrical3D(Uncertainty3D):
    plus = Attribute('meas:Asymmetrical3D.plus', min_occurs=3, max_occurs=3)
    minus = Attribute('meas:Asymmetrical3D.minus', min_occurs=3, max_occurs=3)


@VO('meas:Bounds3D')
class Bounds3D(Uncertainty3D):
    lo_limit = Attribute('meas:Bounds3D.loLimit', min_occurs=3, max_occurs=3)
    hi_limit = Attribute('meas:Bounds3D.hiLimit', min_occurs=3, max_occurs=3)


@VO('meas:Ellipse')
class Ellipse(Uncertainty2D):
    semi_axis = Attribute('meas:Ellipse.semiAxis', min_occurs=2, max_occurs=2)
    pos_angle = Attribute('meas:Ellipse.posAngle', min_occurs=1, max_occurs=1)


@VO('meas:Ellipsoid')
class Ellipsoid(Uncertainty3D):
    semi_axis = Attribute('meas:Ellipsoid.semiAxis', min_occurs=3, max_occurs=3)
    pos_angle = Attribute('meas:Ellipsoid.posAngle', min_occurs=2, max_occurs=2)


@VO('meas:Matrix')
class Matrix(BaseType):
    pass


@VO('meas:Matrix2x2')
class Matrix2x2(Matrix):
    m11 = Attribute('meas:Matrix2x2.m11', min_occurs=1, max_occurs=1)
    m12 = Attribute('meas:Matrix2x2.m12', min_occurs=1, max_occurs=1)
    m21 = Attribute('meas:Matrix2x2.m21', min_occurs=1, max_occurs=1)
    m22 = Attribute('meas:Matrix2x2.m22', min_occurs=1, max_occurs=1)


@VO('meas:Matrix3x3')
class Matrix3x3(Matrix):
    m11 = Attribute('meas:Matrix3x3.m11', min_occurs=1, max_occurs=1)
    m12 = Attribute('meas:Matrix3x3.m12', min_occurs=1, max_occurs=1)
    m13 = Attribute('meas:Matrix3x3.m13', min_occurs=1, max_occurs=1)
    m21 = Attribute('meas:Matrix3x3.m21', min_occurs=1, max_occurs=1)
    m22 = Attribute('meas:Matrix3x3.m22', min_occurs=1, max_occurs=1)
    m23 = Attribute('meas:Matrix3x3.m23', min_occurs=1, max_occurs=1)
    m31 = Attribute('meas:Matrix3x3.m31', min_occurs=1, max_occurs=1)
    m32 = Attribute('meas:Matrix3x3.m32', min_occurs=1, max_occurs=1)
    m33 = Attribute('meas:Matrix3x3.m33', min_occurs=1, max_occurs=1)


@VO('meas:CovarianceMatrix2D')
class CovarianceMatrix2D(Uncertainty2D):
    matrix = Attribute('meas:CovarianceMatrix2D.matrix', min_occurs=1, max_occurs=1)


@VO('meas:CovarianceMatrix3D')
class CovarianceMatrix3D(Uncertainty3D):
    matrix = Attribute('meas:CovarianceMatrix3D.matrix', min_occurs=1, max_occurs=1)


@VO('meas:Measure')
class Measure(BaseType):
    pass


@VO('meas:CoordMeasure')
class CoordMeasure(Measure):
    coord = Attribute('meas:CoordMeasure.coord', min_occurs=1, max_occurs=1)
    error = Composition('meas:CoordMeasure.error', min_occurs=0, max_occurs=1)


@VO('meas:Error')
class Error(BaseType):
    pass


@VO('meas:Error1D')
class Error1D(Error):
    stat_error = Attribute('meas:Error1D.statError', min_occurs=0, max_occurs=1)
    sys_error = Attribute('meas:Error1D.sysError', min_occurs=0, max_occurs=1)
    ran_error = Attribute('meas:Error1D.ranError', min_occurs=0, max_occurs=1)


@VO('meas:Error2D')
class Error2D(Error):
    stat_error = Attribute('meas:Error2D.statError', min_occurs=0, max_occurs=1)
    sys_error = Attribute('meas:Error2D.sysError', min_occurs=0, max_occurs=1)
    ran_error = Attribute('meas:Error2D.ranError', min_occurs=0, max_occurs=1)


@VO('meas:Error3D')
class Error3D(Error):
    stat_error = Attribute('meas:Error3D.statError', min_occurs=0, max_occurs=1)
    sys_error = Attribute('meas:Error3D.sysError', min_occurs=0, max_occurs=1)
    ran_error = Attribute('meas:Error3D.ranError', min_occurs=0, max_occurs=1)


@VO('meas:GenericCoordMeasure')
class GenericCoordMeasure(CoordMeasure):
    pass


@VO('meas:Position')
class Position(CoordMeasure):
    pass


@VO('meas:Position1D')
class Position1D(Position):
    pass


@VO('meas:Position2D')
class Position2D(Position):
    pass


@VO('meas:Position3D')
class Position3D(Position):
    pass


@VO('meas:SpectralCoordMeasure')
class SpectralCoordMeasure(CoordMeasure):
    pass


@VO('meas:TimeMeasure')
class TimeMeasure(CoordMeasure):
    pass


@VO('meas:Polarization')
class Polarization(Measure):
    coord = Attribute('meas:Polarization.coord', min_occurs=1, max_occurs=1)


@VO('meas:StdPosition')
class StdPosition(Position):
    pass


@VO('meas:GenTimeMeasure')
class GenTimeMeasure(TimeMeasure):
    pass


@VO('meas:StdTimeMeasure')
class StdTimeMeasure(TimeMeasure):
    pass
