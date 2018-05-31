from __future__ import division, print_function
import numpy as np
import scipy.io.wavfile as wav
import pyaudio
import wave
import sys

def playpulses(filename):

    '''
    play recorded sound that was saved to .txt file;
    the time-series data is returned as a [Ntx2] array ts
    '''

    # parameters
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100 #22050 #
    deltaT = 1.0/RATE

    # first construct wavfile
    ts = np.loadtxt(filename)
    scaled = np.int16(ts[:,1] * 32767)
    wav.write('temp.wav', RATE, scaled)

    wf = wave.open('temp.wav', 'rb')


    # instantiate pyaudio
    p = pyaudio.PyAudio()

    # open stream
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=CHANNELS,
                    rate=wf.getframerate(),
                    output=True,
                    frames_per_buffer=CHUNK)

    # FORMAT
    # RATE

    data = wf.readframes(CHUNK)

    while data != b'':
        stream.write(data)
        data = wf.readframes(CHUNK)

    stream.stop_stream()
    stream.close()

    p.terminate()

    return ts
