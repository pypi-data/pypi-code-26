
import libcppjieba

def cut(sentence):
       it = libcppjieba.tag(sentence)
       return iter(it)

lcut = libcppjieba.tag