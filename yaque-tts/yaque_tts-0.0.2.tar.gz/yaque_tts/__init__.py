# *_* coding:utf-8 *_*

import yaque_tts

def play():
    audio_root = raw_input("请输入声源路径")
    index_root = raw_input("请输入索引源路径")
    text = raw_input("请输入中文\n")
    yaque_tts.Yaque_Tts(audio_root, index_root).play(text)

# play()