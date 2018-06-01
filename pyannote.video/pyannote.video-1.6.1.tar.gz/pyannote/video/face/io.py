#!/usr/bin/env python
# encoding: utf-8

# The MIT License (MIT)

# Copyright (c) 2018 CNRS

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# AUTHORS
# Herve BREDIN - http://herve.niderb.fr


import numpy as np
import pandas as pd
from pyannote.core import Segment
from pyannote.core import Annotation
from pyannote.core import SlidingWindow
from pyannote.core import SlidingWindowFeature


def load_tracking(path):
    """Load tracking face results

    Parameter
    ---------
    path : str
        Path to `pyannote-face track` output.

    Returns
    -------
    time_ranges : `pyannote.core.Annotation`
    detections : dict, indexed by `track_id`
        Dictionary indexed by `track_id`. Each value is a 4-dimensional
        `SlidingWindowFeature` containing face position in the following order:
        "left", "top", "right", "bottom".

    Example
    -------
    >>> time_ranges, detections = load_face_track('track.txt')
    >>> for time_range, track_id in time_ranges.itertracks():
    ...      faces = detections[track_id]
    ...      for t, face in faces:
    ...          # do something smart...

    See also
    --------
    `SlidingWindowFeature.crop`

    """

    # load tracking results into a DataFrame with the following columns
    # t      = elapsed time since the beginning of the video (unit = seconds)
    # track  = all faces belonging to the same tracklet share this same id
    # left   = bounding box left boundary (unit = ratio of frame width)
    # top    = bounding box top boundary (unit = ratio of frame height)
    # right  = same as left, but right :)
    # bottom = same as top, but right :)
    names = ['t', 'track_id', 'left', 'top', 'right', 'bottom', 'status']
    dtype = {'left': np.float32, 'top': np.float32,
             'right': np.float32, 'bottom': np.float32}
    tracking = pd.read_table(path, delim_whitespace=True, header=None,
                             names=names, dtype=dtype)

    # sort rows in chronological order
    tracking = tracking.sort_values('t')

    # `Annotation` meant to store face tracks time ranges
    time_ranges = Annotation()

    # `dict` meant to store face tracks coordinates
    positions = dict()

    # group detections by face track
    face_tracks = tracking.groupby(by='track_id')

    # estimate tracking rate using the following heuristic:
    # estimate median time difference between consecutive detections)
    tracking_step = np.nanmedian([np.median(np.diff(detections.t))
                                  for _, detections in face_tracks])

    # iterate over each face track
    for track_id, detections in face_tracks:

        # estimate face track time range
        time_range = Segment(min(detections.t), max(detections.t))

        # store face track time rang
        time_ranges[time_range, track_id] = track_id

        # ensure we have detection for all time step (otherwise, interpolate)
        i, interpolations = 0, []

        # loop on every time step
        for t in np.arange(time_range.start, time_range.end, tracking_step):

            # this is the next available detection
            next_detection = detections.iloc[i]
            next_detection = next_detection.drop('status')
            next_t = next_detection.t

            # if it is too far away in time, interpolate
            if next_t - t > 0.5 * tracking_step:
                current_detection = detections.iloc[i - 1]
                current_detection = current_detection.drop('status')
                current_t = current_detection.t
                alpha = 1. - (t - current_t) / (next_t - current_t)
                interpolation = alpha * current_detection + \
                                (1. - alpha) * next_detection
                interpolation['status'] = 'interpolated'
                interpolations.append(interpolation)
            # otherwise, jump to next detection
            else:
                i += 1

        # add missing (interpolated) detections
        detections = pd.concat([detections, pd.DataFrame(interpolations)],
                               ignore_index=True)
        detections = detections.sort_values('t').set_index('t')

        # store detections as SlidingWindowFeature instances
        window = SlidingWindow(start=time_range.start,
                               duration=tracking_step,
                               step=tracking_step)

        data = detections.drop(['track_id', 'status'], axis=1).values
        positions[track_id] = SlidingWindowFeature(data, window)

    return time_ranges, positions


# TODO. temporal smoothing detections
# TODO. update positions to match the behavior of syncnet own detector
