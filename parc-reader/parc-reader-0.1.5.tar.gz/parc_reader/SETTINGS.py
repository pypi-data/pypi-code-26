from os import path

CLONE_PATH = path.abspath(path.join(path.dirname(__file__), '..'))

RAW_DIR = path.join(CLONE_PATH, 'masked_raw')
RAW_TRAIN_DIR = path.join(RAW_DIR, 'train')
RAW_TEST_DIR = path.join(RAW_DIR, 'test')
RAW_DEV_DIR = path.join(RAW_DIR, 'dev')

CORENLP_DIR = path.join(CLONE_PATH, 'CoreNLP')
CORENLP_TRAIN_DIR = path.join(CORENLP_DIR, 'train')
CORENLP_TEST_DIR = path.join(CORENLP_DIR, 'test')
CORENLP_DEV_DIR = path.join(CORENLP_DIR, 'dev')

PARC_DIR = path.join(CLONE_PATH, 'parc3')
PARC_TRAIN_DIR = path.join(PARC_DIR, 'train')
PARC_DEV_DIR = path.join(PARC_DIR, 'dev')
PARC_TEST_DIR = path.join(PARC_DIR, 'test')

BNP_DIR = path.join(CLONE_PATH, 'bbn-pcet')
PROPBANK_DIR = '/home/ndg/users/enewel3/propbank_1'
PROPBANK_DIR = path.join(CLONE_PATH, 'propbank_1')

ROLES = ['source', 'cue', 'content']
