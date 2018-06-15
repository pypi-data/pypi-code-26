"""
A python module that provides tools for position and orientation tracking
inside the SoundScape Renderer (SSR) using the OptiTrack optical tracking system.

This module contains the abstract class _Bridge and its subclasses.
_Bridge is a thread class that includes the actual sequence, whereas the subclasses implement
different applications of a connection between the SSR and a tracking system.
In any subclass of _Bridge the functions to receive and send data need to be defined
according to the desired application.
"""

from __future__ import print_function
import sys
import threading
import socket
from time import sleep
from abc import ABCMeta, abstractmethod # for abstract classes and methods
import numpy as np

from .opti_client import Quaternion

class _Bridge(threading.Thread):
    """An abstract class which implements a threading approach to receive and send data.
       To implement the functionality to send and receive the desired data,
       subclasses need to define the functions _receive and _send.

       .. note:: The returns of _receive have to be the input of _send.
    """

    # Python2 compatible way to declare an abstract class
    __metaclass__ = ABCMeta

    def __init__(
            self, optitrack, ssr, data_limit=500, timeout=0.01, *args,
            **kwargs):

        # call contructor of super class (threading.Thread)
        super(_Bridge, self).__init__(*args, **kwargs)

        # event triggered to stop execution
        self._quit = threading.Event()

        # interfaces
        self._optitrack = optitrack
        self._ssr = ssr

        # storing older data
        self._data = []  # the data buffer itself
        self._data_limit = data_limit  # maximum number of entries
        self._data_lock = threading.Lock()  # mutex to block access
        self._data_available = threading.Event()  # event for new data

        # timeout
        self._timeout = timeout  # timeout in seconds

    def get_last_data(self, num=None):
        """Returns a list of data received from the OptiTrack system."""
        if not num:
            num = self._data_limit
        return self._data[-num:]

    def clear_data(self):
        """Clears buffer"""
        if self._data_available.is_set():
            with self._data_lock:  # lock the mutex
                self._data = []
                self._data_available.clear()

    def run(self):
        while not self._quit.is_set():
            try:
                packet = self._receive()
            except socket.error:  # thrown if not packet has arrived
                sleep(self._timeout)
            except (KeyboardInterrupt, SystemExit):
                self._quit.set()
            else:
                # save data
                with self._data_lock:
                    self._data.append(packet)
                    self._data = self._data[-self._data_limit:]
                self._data_available.set()
                # send data
                self._send(packet)

    def stop(self):
        self._quit.set()  # fire event to stop execution

    @abstractmethod
    def _receive(self):
        return

    @abstractmethod
    def _send(self, packet):
        return

class HeadTracker(_Bridge):
    """
    A class for using the OptiTrack system as a head tracker for the SSR.

    Attributes
    ----------
    optitrack : class object
        Object of class OptiTrackClient.
    ssr : class object
        Object of class SSRClient.
    rb_id : int, optional
        ID of the rigid body to receive data from.
    angle : int, optional
        angle which is used for head rotation
        
        * +1 - positive yaw
        * -1 - negative yaw
        * +2 - positive pitch
        * -2 - negative pitch
        * +3 - positive roll
        * -3 - negative roll
    """

    def __init__(self, optitrack, ssr, rb_id=0, angle=1, *args, **kwargs):
        # call contructor of super class (_Bridge)
        super(HeadTracker, self).__init__(optitrack, ssr, *args, **kwargs)
        # selects which rigid body from OptiTrack is the head tracker
        self._rb_id = rb_id
        self._angle = angle
        # origin and orientation of world coordinate system
        self._origin = np.array((0, 0, 0))
        self._orientation = Quaternion(1, 0, 0, 0)

    def calibrate(self):
        """
        Use current position and orientation of head tracker to set the origin
        and orientation of the world coordinate system.
        """
        self._origin, self._orientation, _ = self._optitrack.get_rigid_body(self._rb_id)

    def _receive(self):
        self._ssr.recv_ssr_returns()
        pos, ori, time_data = self._optitrack.get_rigid_body(self._rb_id)
        # apply coordinate transform
        pos = pos - self._origin
        ori = self._orientation.conjugate * ori  # not commutative

        return pos, ori.yaw_pitch_roll, time_data

    def _send(self, data):
        _, ypr, _ = data  # (pos, ypr, time_data)
        alpha = np.sign(self._angle)*ypr[np.absolute(self._angle)-1]*180/np.pi+90
        self._ssr.set_ref_orientation(alpha)

class LocalWFS(_Bridge):
    """
    A class for using the OptiTrack system to track the listener position
    in the SSR for local sound field synthesis.

    The first SSR instance (ssr) shifts the reference position and the
    reference offset position of the real reproduction setup, such that
    it emulates the movement a virtual source array placed around the
    listener.

    The second SSR instance (ssr_virt_repr) shifts the reference position of
    aforementioned point sources as the virtual reproduction setup
    in relation to the real sources based on audio files.

    Attributes
    ----------
    optitrack : class object
        Object of the class OptiTrackClient.
    ssr : class object
        First SSR instance as object of class SSRClient.
    ssr_virt_repr : class object
        Second SSR instance as object of the class SSRClient.
    rb_id : int, optional
        ID of the rigid body to receive data from.
    """
    def __init__(self, optitrack, ssr, ssr_virt_repr, rb_id=0, *args, **kwargs):
        # call contructor of super class
        super(LocalWFS, self).__init__(optitrack, ssr, *args, **kwargs)
        # selects which rigid body from OptiTrack is the tracker
        self._rb_id = rb_id
        # second ssr instance feat. virtual sources as reproduction setup
        self._ssr_virt_repr = ssr_virt_repr
        # reference orientation of this instance has to be changed once
        # in order to compensate for the SSRs standard reference orientation shift
        self._ssr_virt_repr.set_ref_orientation(0)

        # self._create_virtual_sources()

    def _create_virtual_sources(self):
        """Create a specified amount of new sources via network connection to the SSR.
        """
        for src_id in range(1, self._N+1):
            self._ssr.src_creation(src_id)

    def _receive(self):
        """Get position data of rigid body from OptiTrack system

        Returns
        -------
        center : list
            Rigid body position data.
            Consists of x, y, z coordinates of Motive`s coordinate system.
        """
        self._ssr.recv_ssr_returns()
        self._ssr_virt_repr.recv_ssr_returns()

        center, _, _ = self._optitrack.get_rigid_body()

        return center

    def _send(self, center):
        """Send reference position data to both SSR instance.
        """
        self._ssr.set_ref_position(-center[0], -center[1])
        self._ssr.set_ref_offset_position(center[0], center[1])
        self._ssr_virt_repr.set_ref_position(center[0], center[1])
