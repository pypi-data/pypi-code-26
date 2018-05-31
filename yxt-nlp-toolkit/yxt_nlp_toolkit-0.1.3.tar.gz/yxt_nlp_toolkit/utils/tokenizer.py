import jieba
import jieba.posseg as posseg


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
