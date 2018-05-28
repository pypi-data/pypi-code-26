#coding=utf-8

from fmtlabels.fmt import analyze
from fmtlabels.fmt import marshal

def lbl_fmtlines(output, category, input):
    for text in input:
        if text == '':
            continue
        data = {text : analyze(category, text)}
        marshal(output, data)
