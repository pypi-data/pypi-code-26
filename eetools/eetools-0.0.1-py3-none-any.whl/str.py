#!/usr/bin/env python
# -*- coding:utf-8 -*-
import random, string
def GenString(length=10):
	numOfNum = random.randint(1,length-1)
	numOfLetter = length - numOfNum
	#选中numOfNum个数字
	slcNum = [random.choice(string.digits) for i in range(numOfNum)]
	#选中numOfLetter个字母
	slcLetter = [random.choice(string.ascii_letters) for i in range(numOfLetter)]
	#打乱这个组合
	slcChar = slcNum + slcLetter
	random.shuffle(slcChar)
	#生成密码
	genPwd = ''.join([i for i in slcChar])
	return genPwd

str = GenString(10)
print(str)