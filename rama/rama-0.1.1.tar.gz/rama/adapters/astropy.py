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

"""
This module provides astropy-specific adapters. See `~rama.adapters` for more information on adapters.
"""
import logging

from astropy.coordinates import SkyCoord
from astropy.time import Time
from astropy.units import Quantity, UnitTypeError

import numpy
from numpy import nan_to_num

from rama.models import coordinates

LOG = logging.getLogger(__name__)


class SkyCoordAdapter:
    """
    A an adapter for sky coordinates. The initializer takes a standard
    :py:class:`~rama.models.coordinates.SpaceCoord` instance and returns an astropy.coordinates.SkyCoord object based
    on the contents of the original instance.
    """

    def __new__(cls, stc_position_coord):
        try:
            frame = stc_position_coord.frame.space_ref_frame.lower()
            equinox = stc_position_coord.frame.equinox
        except (AttributeError, ValueError):
            frame = "icrs"
            equinox = None

        try:  # FIXME This only works with equatorial coordinates. Implement for other coordinates as well
            ra = stc_position_coord.ra
            dec = stc_position_coord.dec
            sky_coord = SkyCoord(frame=frame, equinox=equinox, ra=ra, dec=dec)
            return sky_coord
        except (AttributeError, UnitTypeError, ValueError) as exc:
            LOG.warning(f"Can't apply adapter: {exc}")
            return stc_position_coord


# FIXME this is full of hacks and shortcuts
class TimeAdapter:
    """
    Adapter for time objects and arrays. It takes a standard :py:class:`~rama.models.coordinates.TimeStamp` instance
    and returns an astropy Time quantity.
    """
    def __new__(cls, stc_time_coord):
        # FIXME I can't figure out how to make astropy parse iso times as time columns, so I have to break
        # them down and extract times
        date = stc_time_coord.date
        if not isinstance(date, Quantity):
            quantity = False
            time = date.tolist()
        else:
            quantity = True
            time = date

        try:
            scale = 'tt' if stc_time_coord.frame is None else stc_time_coord.frame.timescale.lower()
            t_format = "isot" if isinstance(stc_time_coord, coordinates.ISOTime) else "jd"
        except AttributeError:
            scale = None
            t_format = None

        try:
            # Astropy doesn't support nan in Time objects yet (should be coming in Astropy 3)
            if not quantity:
                time = nan_to_num(numpy.array(time))
            else:
                time = nan_to_num(time)
            time = Time(time, scale=scale, format=t_format)
            time.name = stc_time_coord.date.name
            return time
        except AttributeError:
            return stc_time_coord
