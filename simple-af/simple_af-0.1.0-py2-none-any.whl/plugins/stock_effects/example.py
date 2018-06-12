import random
from simple_af.model import Effect, Scene, MultiEffect
from simple_af.state import STATE

class SolidBackground(Effect):
    """Always return a singular color. Can be bound top/bottom and
    left-right (wrap-around not supported yet)
    """

    def __init__(self, color=(255, 0, 0), start_col=0, end_col=None, start_row=0, end_row=None):
        Effect.__init__(self)
        self.color = color
        self.slice = (slice(start_row, end_row), slice(start_col, end_col))
        print "Created with color", self.color

    def next_frame(self, pixels, t):
        pixels[self.slice] = self.color

class MovingSlice(Effect):
    """Always return a singular color. Can be bound top/bottom and
    left-right (wrap-around not supported yet)
    """

    def __init__(self, color=(255, 0, 0), start_row=0, length=10, col=0):
        Effect.__init__(self)
        self.color = color
        self.current_row = start_row
        self.col = col
        self.length= length

    def next_frame(self, pixels, t):
        if self.current_row+self.length>113:
            pixels[self.current_row:] = self.color
            pixels[0:self.length+self.current_row-113] = self.color
        else:
            pixels[self.current_row:self.current_row+self.length] = self.color
        self.current_row = (self.current_row) + 1 % 113


class SelfDestructingSolidColor(Effect):
    def __init__(self, note, velocity):
        Effect.__init__(self)
        #self.color = tuple(self._get_color(note, min(velocity*2,200), i) for i in range(3))
        self.color = (0,0,min(velocity*2,200))
        self.rendered = 3

    def next_frame(self, pixels, t):
        pixels[:] = self.color
        self.rendered -= 1

    def is_completed(self, t):
        return self.rendered <= 0

    def _get_color(self, note, velocity, param):
        return velocity if note%3 == param else 0


class MovingColor(Effect):
    def __init__(self, drum_hit, columns):
        Effect.__init__(self)
        #self.color = tuple(self._get_color(note, min(velocity*2,255, 80), i) for i in range(3))
        self.color = (
            0,
            self._get_color(drum_hit.note, min(drum_hit.velocity*2,255, 80), 1),
            self._get_color(drum_hit.note, min(drum_hit.velocity*2,255, 80), 0),
            )
        self.location = 0
        self.columns = columns

    def next_frame(self, pixels, t):
        #pixels[self.location:self.location+2,:] = self.color
        pixels[STATE.layout.rows/2+self.location:STATE.layout.rows/2+self.location+2,self.columns] = self.color
        pixels[STATE.layout.rows/2-self.location-2:STATE.layout.rows/2-self.location,self.columns] = self.color
        self.location += 1

    def is_completed(self, t):
        return self.location >= STATE.layout.rows/2-1

    def _get_color(self, note, velocity, param):
        return velocity if note%2 == param else 0

SCENES = [
    #Scene(
    #    "movingslice",
    #    effects=[MovingSlice()]
    #),
    #Scene(
    #    "solidwhite",
    #    effects=[
    #        SolidBackground(color=(150,0,0)),
    #        MidiListener()
    #    ]
    #),

]