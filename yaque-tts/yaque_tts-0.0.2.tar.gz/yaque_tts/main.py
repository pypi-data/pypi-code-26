# *_* coding:utf-8 *_*

import read_audio as ra
import read_word_index as rwi
import audio_play as ap

read_audio = ra.ReadAudio("yaque_tts/yali")
file_name_data_lists, audio_data_lists = read_audio.get_data()

read_word_index = rwi.ReadWordIndex("yaque_tts/zh_list")
phoneticize_index_lists, word_index_lists = read_word_index.get_read_word_index()

audio_play = ap.AudioPlay()

play_input = raw_input("请输入内容：")
while play_input != '0':
    cmd_list = []
    i = 0
    print(len(play_input))
    while(i != len(play_input)):
        cmd_list.append(play_input[i] + play_input[i + 1] + play_input[i + 2])
        i = i + 3

    play_data_lists = []
    for i in range(len(cmd_list)):
        for j in range(len(word_index_lists)):
            if cmd_list[i] == word_index_lists[j]:
                for k in range(len(file_name_data_lists)):
                    if file_name_data_lists[k].split(".")[0] == phoneticize_index_lists[j]:
                        play_data_lists.append(audio_data_lists[k])

    audio_play.play(play_data_lists)
    play_input = raw_input("请输入内容：")