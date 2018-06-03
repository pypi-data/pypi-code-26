#!/usr/bin/env python3.6


class Converter():
    def __init__(self):

        self.bng_to_eng = {'১' : '1', '২' : '2', '৩' : '3', '৪' : '4', '৫' : '5', '৬' : '6', '৭' : '7', '৮' : '8', '৯' : '9', '০' : '0'}
        self.eng_to_bng = {'1' : '১', '2' : '২', '3' : '৩', '4' : '৪',  '5' : '৫', '6' : '৬', '7' : '৭', '8' : '৮', '9' : '৯', '0' : '০'}

    def convert_eng_to_bng(self, engNum):
        str_num = str(engNum)
        numArray = [str(i) for i in str(str_num)]
        converted_num = " "

        i = 0
        while len(numArray) > i:
            try:
                converted_num += self.eng_to_bng[numArray[i]]
            except:
                converted_num += numArray[i]
            i += 1

        return converted_num

    def convert_bng_to_eng(self, bngNum):
        str_num = str(bngNum)
        numArray = [str(i) for i in str(str_num)]
        converted_num = " "

        i = 0
        while len(numArray) > i:
            try:
                converted_num += self.bng_to_eng[numArray[i]]
            except:
                converted_num += numArray[i]
            i += 1

        return converted_num