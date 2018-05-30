# *_* coding:utf-8 *_*

import read_audio as ra
import read_word_index as rwi
import audio_play as ap

class Yaque_Tts(object):

    def __init__(self, audio_root, index_root):
        read_audio = ra.ReadAudio(audio_root)
        self.file_name_data_lists, self.audio_data_lists = read_audio.get_data()

        read_word_index = rwi.ReadWordIndex(index_root)
        self.phoneticize_index_lists, self.word_index_lists = read_word_index.get_read_word_index()

        self.audio_play = ap.AudioPlay()

    def play(self, play_input):
        cmd_list = []
        i = 0
        print(len(play_input))
        while (i != len(play_input)):
            cmd_list.append(play_input[i] + play_input[i + 1] + play_input[i + 2])
            i = i + 3

        play_data_lists = []
        for i in range(len(cmd_list)):
            for j in range(len(self.word_index_lists)):
                if cmd_list[i] == self.word_index_lists[j]:
                    for k in range(len(self.file_name_data_lists)):
                        if self.file_name_data_lists[k].split(".")[0] == self.phoneticize_index_lists[j]:
                            play_data_lists.append(self.audio_data_lists[k])

        self.audio_play.play(play_data_lists)