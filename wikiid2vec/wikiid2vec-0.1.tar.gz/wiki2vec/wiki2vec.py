import gensim
import math
import requests
import os.path
from tqdm import tqdm

import config

import logging
import os.path
import sys
import multiprocessing
from gensim.models import Word2Vec
from gensim.models.word2vec import LineSentence
from gensim.corpora import WikiCorpus

program = os.path.basename(sys.argv[0])
logger = logging.getLogger(program)

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s')
logging.root.setLevel(level=logging.INFO)
logger.info("running %s" % ' '.join(sys.argv))


"""
    thanks for https://yudiwbs.wordpress.com/2018/03/31/word2vec-wikipedia-bahasa-indonesia-dengan-python-gensim/
"""


class Wiki2Vec:

    def __init__(self):
        pass

    def training(self, namaFileInput, namaFileOutput):
        model = Word2Vec(LineSentence(namaFileInput), size=400, window=5, min_count=5,
                         workers=multiprocessing.cpu_count())

        model.init_sims(replace=True)
        model.save(namaFileOutput)

    def extract(self, namaFileInput, namaFileOutput, **kwargs):
        space = " "
        output = open(namaFileOutput, 'w')
        i = 0
        wiki = WikiCorpus(namaFileInput, lemmatize=False, dictionary={}, lower=True,  **kwargs)
        for text in wiki.get_texts():
            output.write(' '.join(text) + '\n')
            i = i + 1
            if i % 10000 == 0:
                logger.info("Saved " + str(i) + " articles")

        logger.info("Finished Saved " + str(i) + " articles")

        output.close()

    def download(self, file_name_url, target_name=None):
        response = requests.get(file_name_url, stream=True)
        if not target_name:
            target_name = file_name_url.split("/")[-1:][0]

        if not os.path.exists(target_name):

            # Total size in bytes.
            total_size = int(response.headers.get('content-length', 0))
            block_size = 1024
            wrote = 0
            with open(target_name, 'wb') as f:
                for data in tqdm(response.iter_content(block_size), total=math.ceil(total_size // block_size), unit='KB',
                                 unit_scale=True):
                    wrote = wrote + len(data)
                    f.write(data)
            if total_size != 0 and wrote != total_size:
                print("ERROR, something went wrong")

        return target_name

    def setup(self):
        file_name = self.download(config.WIKI_FILE_URL)
        self.extract(file_name, config.FILE_NAME_WIKI)
        self.training(config.FILE_NAME_WIKI, config.FILE_NAME_OUTPUT_WIKI)

    def load_model(self, file_name=None):
        if not file_name:
            file_name = config.FILE_NAME_OUTPUT_WIKI
        return gensim.models.Word2Vec.load(file_name)


if __name__ == '__main__':
    wiki2vec = Wiki2Vec()
    wiki2vec.setup()
