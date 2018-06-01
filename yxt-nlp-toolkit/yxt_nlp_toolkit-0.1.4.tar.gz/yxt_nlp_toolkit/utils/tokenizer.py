import jieba
import jieba.posseg as posseg
from .str_algo import is_ascii_alpha, is_digit


def token_stream(file_or_files, with_postag=False):
    if isinstance(file_or_files, str):
        files = (file_or_files,)
    else:
        files = tuple(file_or_files)
    cut_func = posseg.cut if with_postag else jieba.cut
    for file in files:
        with open(file, 'r') as f:
            for line in f:
                yield from cut_func(line)


def tokenizer(text, with_postag=False, to_upper=True, skip_space=False, cut_digits=False, cut_ascii=False):
    cut_func = posseg.cut if with_postag else jieba.cut
    for seg in cut_func(text):
        if with_postag:
            word, postag = seg.word, seg.flag
        else:
            word, postag = seg, None
        if skip_space and word == ' ':
            continue
        if to_upper:
            word = word.upper()

        if (cut_digits and all(is_digit(c) for c in word)) or (cut_ascii and all(is_ascii_alpha(c) for c in word)):
            for c in word:
                if with_postag:
                    yield c, postag
                else:
                    yield c
        else:
            if with_postag:
                yield word, postag
            else:
                yield word
