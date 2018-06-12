import mido
from threading import Thread
from collections import namedtuple

from simple_af import osc_utils
from simple_af.model import Effect, MultiEffect
from simple_af.state import STATE
bass=36

tom_1 = 48
tom_2 = 47
floor_tom = 43

cymble_crash_bell = 55
cymble_crash_crash = 49
cymble_crash_hit = 59

cymble_ride_bell = 53
cymble_ride_crash = 52
cymble_ride_hit = 51

snare_hit = 38
snare_cross = 37
snare_rim = 40

closed_hit_high_hat = 42
closed_crash_high_hat = 86
open_hit_high_hat = 46
open_crash_high_hat = 85
high_hat_close=44

def listen_for_midi(backend='mido.backends.rtmidi_python', port=None, virtual=None):
    mido.set_backend(name=backend, load=True)

    midi_thread = Thread(target=_forward_midi, name="MidoListeningThread", args=(port, virtual))
    midi_thread.setDaemon(True)
    midi_thread.start()

def _forward_midi(port=None, virtual=None):
    osc_client = osc_utils.get_osc_client()
    print "Opening midi port for input. Port:", port, "Virtual: ", virtual
    with mido.open_input(port, virtual=virtual) as midi_in:
        for msg in midi_in:
            if msg.type in ['note_on'] and msg.velocity > 0:
                osc_utils.send_simple_message(osc_client, path="/input/midi", data=[msg.type, msg.note, msg.velocity])

DrumHit = namedtuple("DrumHit", ["note", "velocity"])


class AbstractMidiListener(MultiEffect):
    def before_rendering(self, pixels, t):
        super(AbstractMidiListener, self).before_rendering(pixels, t)
        for data in STATE.osc_data.current['midi']:
            self.process_note(pixels, t, data)

    def process_note(self, pixels, t, data):
        pass


#Concrete implementation for midi listener. Pass a function to handle the data
#(There is probably a cleaner pythonic way to do this)
class MidiLauncher(AbstractMidiListener):
    def __init__(self, factory):
        AbstractMidiListener.__init__(self)
        self.factory = factory

    def process_note(self, pixels, t, data):
        self.add_effect(self.factory(data=data, t=t))