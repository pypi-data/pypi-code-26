# *_* coding:utf-8 *_*

import os
import wave

class ReadAudio(object):

    CHUNK = 1024

    def __init__(self, file_path):
        self.file_path = file_path
        self.files_lists = []
        self.audio_data_lists = []
        self.__walk_file()
        self.__read_audio()

    def __walk_file(self):
        dirs = os.listdir(self.file_path)
        for one_file in dirs:
            self.files_lists.append(one_file)

    def __read_audio(self):
        for one_file in self.files_lists:
            wf = wave.open(self.file_path + "/" + one_file, 'r')
            data_list = []
            data = wf.readframes(self.CHUNK)
            while data != '':
                data = wf.readframes(self.CHUNK)
                data_list.append(data)
            self.audio_data_lists.append(data_list)

    def get_data(self):
        return self.files_lists, self.audio_data_lists

# read_audio = ReadAudio("yaque_tts/yali")
# files_list = read_audio.get_data()
# print(files_list)