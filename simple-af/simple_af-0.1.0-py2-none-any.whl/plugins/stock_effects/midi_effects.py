from __future__ import absolute_import

from simple_af.model import Effect, MultiEffect
from simple_af.state import STATE
from simple_af.plugins.stock_effects import bitmap

class DrumHitRow(Effect):
    def __init__(self, data, *args, **kwargs):
        Effect.__init__(self)
        self.color = (255,255,255)
        self.column_location=STATE.layout.rows-1
        self.row=0
        drum_hit = data.note
        if(drum_hit==36):
            #bass
            self.row=7
        elif(drum_hit in [42, 44, 46, 85, 86]):
            #high hat
            self.row=0
            if(drum_hit==42):
                self.color = (0,255,0)
            elif(drum_hit==44):
                self.color = (0,0,255)
            elif(drum_hit==46):
                self.color = (0,255,255)
            elif(drum_hit==85):
                self.color = (255,255,0)
            elif(drum_hit==86):
                self.color = (255,0,255)
        elif(drum_hit in [55, 49, 59]):
            #cymbal crash
            if(drum_hit==49):
                self.color = (0,255,0)
            elif(drum_hit==55):
                self.color = (0,0,255)
            else:
                self.color = (0,255,255)
            self.row=1
        elif(drum_hit in [53, 52, 51]):
            #ride
            if(drum_hit==51):
                self.color = (0,255,0)
            elif(drum_hit==52):
                self.color = (0,0,255)
            else:
                self.color = (0,255,255)
            self.row=2
        elif(drum_hit in [37, 38, 40]):
            #snare
            if(drum_hit==37):
                self.color = (0,255,0)
            elif(drum_hit==38):
                self.color = (0,0,255)
            else:
                self.color = (0,255,255)
            self.row=3
        elif(drum_hit == 48):
            #tom_1
            self.color = (0,255,0)
            self.row=4
        elif(drum_hit == 47):
            #tom_2
            self.color = (0,0,255)
            self.row=5
        elif(drum_hit == 43):
            #floor_tom
            self.color = (0,0,0)
            self.row = 6


    def next_frame(self, pixels, t):
        pixels[self.column_location, self.row] = self.color
        self.column_location = self.column_location-1

    def is_completed(self, t):
        return self.column_location < 0

class MidiListener(MultiEffect):
    def __init__(self, clazz):
        MultiEffect.__init__(self)
        self.clazz = clazz

    def before_rendering(self, pixels, t):
        super(MidiListener, self).before_rendering(pixels, t)
        for data in STATE.osc_data.current['midi']:
            self.add_effect(self.clazz(data))

class SuperBass(MultiEffect):
    def before_rendering(self, pixels, t):
        super(SuperBass, self).before_rendering(pixels, t)
        for data in STATE.osc_data.current['midi']:
            if(data.note==36): #'B'ass
                self.add_effect(bitmap.DrawMovingBitmap(bitmap.BIG_LETTERS['B'], (255, 255, 255), -1, 0))


DURATION=30
class FlashTony(MultiEffect):
    def before_rendering(self, pixels, t):
        super(FlashTony, self).before_rendering(pixels, t)
        for data in STATE.osc_data.current['midi']:
            if(data.note==36): #'B'ass
                self.add_effect(bitmap.FlashBitmap(bitmap.CACHED_WORDS['TONYx3'], (255, 255, 255), -1, DURATION, 0))

class MidiLetterListener(MultiEffect):
    def before_rendering(self, pixels, t):
        super(MidiLetterListener, self).before_rendering(pixels, t)
        for data in STATE.osc_data.current['midi']:
            #self.add_effect(MovingColor(data,slice(0,None)))
            #self.add_effect(DrumHitRow(data))
            if(data.note==36): #'B'ass
                self.add_effect(bitmap.DrawBitmap(bitmap.LETTERS['B'], (255, 255, 255)))
            else:
            #elif(data.note in [43,47,48]): #'T'om
            #self.add_effect(DrawMovingBitmap(LETTERS_SIX['M'], (255,255,255), -1, 1))
                #self.add_effect(FlashBitmap(LETTERS_SIX['A'], (255,255,255), -1, 30, 1))
                self.add_effect(bitmap.FlashBitmap(bitmap.CACHED_WORDS['DRUM HARDER'], (255, 255, 255), -1, 30, 1))
            #else:
            #    self.add_effect(DrumHitRow(data))