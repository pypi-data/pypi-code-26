# encoding: utf-8

import logging_helper
from uiutil.helper.introspection import calling_base_frame
from ..helper.arguments import grid_and_non_grid_kwargs
from .all import AllMixIn

logging = logging_helper.setup_logging()


class FrameMixIn(AllMixIn):

    FRAME = None  # Redefine in subclass

    def _common_init(self,
                     parent=None,
                     *args,
                     **kwargs):

        self.parent = parent if parent else calling_base_frame(exclude=self)

        # Keep a list of frames added
        self._frames = []

        grid_kwargs, kwargs = grid_and_non_grid_kwargs(frame=self.parent,
                                                       **kwargs)

        # Unfortunately everything Tkinter is written in Old-Style classes so it blows up if you use super!
        self.FRAME.__init__(self, master=self.parent, **kwargs)

        kwargs.update(grid_kwargs)

        AllMixIn.__init__(self, *args, **kwargs)

    def exists(self):
        return self.winfo_exists() != 0

    def exit(self):
        self.cancel_poll()
        self.close_pool()

        for frame in self._frames:
            try:
                frame.exit()

            except Exception as err:
                logging.error(u'Something went wrong while exiting frame: {f}'.format(f=frame))
                logging.error(err)

        self.close()

    def close(self):
        """ Override this to perform steps when the frame is closed. """
        pass

    def register_frame(self,
                       frame_object):
        self._frames.append(frame_object)

    def add_frame(self,
                  frame,
                  **kwargs):
        frame_object = frame(**kwargs)
        self.regsiter_frame(frame_object)
        return frame_object

    def update_geometry(self):
        """ Pass update geometry request to window this frame is a part of. """
        self.parent.update_geometry()
