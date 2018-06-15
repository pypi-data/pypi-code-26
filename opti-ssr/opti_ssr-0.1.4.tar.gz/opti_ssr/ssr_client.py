"""
A python module for controlling the SoundScape Renderer.
"""
from __future__ import print_function
import socket

class SSRClient:
    """
    Establish a TCP/IP4 network connection and send XML messages
    to communicate with a specific instance of the SoundScape Renderer.

    Attributes
    ----------
    ip : str, optional
        IP of the server running thr SSR. By default, it connects to localhost.
    port : int, optional
        Port of SSR Network Interface. By default, port = 4711.
    end_message : str, optional
        Symbol to terminate the XML messages send to SSR. By default, a binary zero.
    """

    def __init__(self, ip='localhost', port=4711, end_message='\0'):
        self._ip = ip
        self._port = port
        self._end_message = end_message

        # IP4 and TCP connection
        self._s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._s.connect((self._ip, self._port))

    def __del__(self):
        self._s.close()
        print("SSRClient: socket closed")

    def src_creation(self, src_id):
        """
        Define a new source.
        """
        new_src = '<request><source new="true" id="{0}" port="0"></source></request>'.format(src_id)+self._end_message
        self._s.send(new_src.encode())

    def set_ref_position(self, x, y):
        """
        Set reference position in meters.
        """
        ref_position = '<request><reference><position x="{0}" y="{1}"/></reference></request>'.format(x, y)+self._end_message
        self._s.send(ref_position.encode())

    def set_ref_offset_position(self, x, y):
        """
        Set reference offset position in meters.
        """
        ref_offset_position = '<request><reference_offset><position x="{0}" y="{1}"/></reference_offset></request>'.format(x, y)+self._end_message
        self._s.send(ref_offset_position.encode())

    def set_ref_orientation(self, alpha):
        """
        Set reference orientation in degrees (zero in positive x-direction).
        """
        ref_orientation = '<request><reference><orientation azimuth="{0}"/></reference></request>'.format(alpha)+self._end_message
        self._s.send(ref_orientation.encode())

    def set_ref_offset_orientation(self, alpha):
        """
        Set reference offset orientation in degrees (zero in positive x-direction).
        """
        ref_offset_orientation = '<request><reference_offset><orientation azimuth="{0}"/></reference_offset></request>'.format(alpha)+self._end_message
        self._s.send(ref_offset_orientation.encode())

    def set_src_position(self, src_id, x, y):
        """
        Change name and position of an existing source.
        """
        position = '<request><source id="{0}" name="SourceMotive{0}"><position x="{1:4.2f}" y="{2:4.2f}"/></source></request>'.format(src_id, x, y)+self._end_message
        self._s.send(position.encode())

    def set_src_orientation(self, src_id, alpha):
        """
        Change orientation of an existing source in degrees (zero in positive x-direction).
        """
        orientation = '<request><source id="{0}"><orientation azimuth="{1}"/></source></request>'.format(src_id, alpha)+self._end_message
        self._s.send(orientation.encode())

    def load_scene(self, path):
        """
        Load a scene from a specified location on the machine running the SSR.
        """
        scene = '<request><scene load="{0}"/></request>'.format(path)+self._end_message
        self._s.send(scene.encode())

    def set_transport_state(self, state):
        """
        Set a specific transport state, namely start, stop or rewind
        to play, pause or rewind all audio tracks of the loaded scene respectively.
        """
        msg = '<request><state transport="{0}"/></request>'.format(state)+self._end_message
        self._s.send(msg.encode())

    def recv_ssr_returns(self):
        """
        Receive messages returned by the SSR.
        """
        msg = self._s.recv(65536)
