# -*- encoding: utf-8 -*-
from os.path import dirname

LOGGING_CONF = 'conf/logging.yaml'
CONFIG_REGRESSOR_LINEAR_FILE = 'conf/conf_regressor_linear.yaml'
CONFIG_CLASSIFY_LOG_FILE = 'conf/conf_classify_log.yaml'
CONFIG_REGRESSOR_RF_FILE = 'conf/conf_regressor_rf.yaml'
CONFIG_CLASSIFY_RF_FILE = 'conf/conf_classify_rf.yaml'
CONFIG_CORR_FILE = 'conf/conf_corr.yaml'
CONFIG_CORR_HANGYAN_FILE = 'conf/conf_corr_hangyan.yaml'

CONFIG_RF_REGRESSOR_TEMPLATE_DIR = 'conf/rf_regressor_template'
CONFIG_HANGYAN_FILE = 'conf/hangyan.yaml'


ROOT_PATH = dirname(dirname(dirname(__file__)))
APP_PATH = dirname(dirname(__file__))

STRING_TYPE = 'string'
BOOL_TYPE = 'boolean'
REAL_TYPES = ['double', 'float']


# scale types
MIN_MAX_SCALER_TYPE = 1
STANDARD_SCALER_TYPE = 2
MAXABS_SCALER_TYPE = 3

# impute types
MEAN_IMPUTER_TYPE = 1
MEDIAN_IMPUTER_TYPE = 2

# feature prep types
CHISQ_FEAT_TYPE = 1
PCA_FEAT_TYPE = 2
DEFAULT_K = 2

# pipe types
CLASSIFICATION = 1
REGRESSION = 2
CORRELATION = 3

# classifier types
LOGISTIC_REGRESSION_CLASSIFIER = 1
RANDOM_FOREST_CLASSIFIER = 2

# regressor types
LINEAR_REGRESSION_REGRESSOR = 1
RANDOM_FOREST_REGRESSOR = 2

# correlation types
PEARSON_CORR = 1
SPEARMAN_CORR = 2
