from __future__ import absolute_import
import simple_af.plugins.midi.midi_utils
from simple_af.state import STATE


def configure_parser(parser, *args, **kwargs):
    parser.add_argument('--midi-port', dest='midi_port', default=None, action='store')
    parser.add_argument('--midi-port-virtual', dest='midi_port_virtual', default=None, action='store')
    parser.add_argument('--midi-backend', dest='midi_backend', default='mido.backends.rtmidi_python', action='store')


def register_listeners(config, *args, **kwargs):
    midi_utils.listen_for_midi(config.midi_backend, config.midi_port, config.midi_port_virtual)


def register_osc_handlers(osc_server):
    def handle_midi(path, tags, args, source):
        STATE.osc_data.accumulating['midi'].append(midi_utils.DrumHit(args[1], args[2]))

    osc_server.addMsgHandler("/input/midi", handle_midi)