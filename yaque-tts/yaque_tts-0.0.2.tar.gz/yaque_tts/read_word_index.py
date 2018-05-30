# *_* coding:utf-8 *_*

class ReadWordIndex(object):

    def __init__(self, file_path="yaque_tts/zh_list"):
        self.file_path = file_path
        self.word_index_lists = []
        self.phoneticize_index_lists = []
        self.read_index()

    def read_index(self):
        index_file = open(self.file_path, "r")
        one_index = index_file.readline()
        while(one_index):
            one_line = one_index.split("	")
            self.word_index_lists.append(one_line[0])
            self.phoneticize_index_lists.append(one_line[1].split("\n")[0])
            one_index = index_file.readline()

    def get_read_word_index(self):
        return self.phoneticize_index_lists, self.word_index_lists

# ReadWordIndex("yaque_tts/zh_list")