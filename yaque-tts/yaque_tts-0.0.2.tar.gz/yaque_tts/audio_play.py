# *_* coding:utf-8 *_*

import pyaudio

class AudioPlay(object):

    def play(self, audio_data_lists):
        p = pyaudio.PyAudio()
        out_stream = p.open(format=p.get_format_from_width(2),
                        channels=1,
                        rate=44100,
                        output=True)

        for audio_data in audio_data_lists:
            for data in audio_data:
                out_stream.write(data)

        out_stream.stop_stream()
        out_stream.close()
        p.terminate()