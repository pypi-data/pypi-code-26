import numpy as np
import pandas as pd
from collections import OrderedDict
import re
import sys
import os
import io
import csv

from sklearn.utils import shuffle
from sklearn.metrics import roc_auc_score, roc_curve, auc
from scipy import stats

from keras import initializers
from keras import backend as K, initializers, regularizers, constraints
from keras.utils import np_utils
from keras.optimizers import SGD, Adam, RMSprop
from keras.callbacks import EarlyStopping
from keras.models import load_model
from keras.models import Sequential, Model
from keras.layers import Dense, Embedding, Activation, merge, Input, Lambda, Reshape,BatchNormalization
from keras.layers import Convolution1D, Flatten, Dropout, MaxPool1D, GlobalAveragePooling1D
from keras.layers import LSTM, GRU, TimeDistributed, Bidirectional
from keras.utils.np_utils import to_categorical
from keras.engine.topology import Layer

from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import SGDClassifier,LogisticRegressionCV
from sklearn.feature_extraction.text import TfidfVectorizer,CountVectorizer
from sklearn.feature_selection import SelectKBest, chi2
from sklearn.linear_model import LogisticRegressionCV
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split

from gensim.models import Word2Vec

aa_idx = OrderedDict([
    ('A', 1),
    ('C', 2),
    ('E', 3),
    ('D', 4),
    ('G', 5),
    ('F', 6),
    ('I', 7),
    ('H', 8),
    ('K', 9),
    ('M', 10),
    ('L', 11),
    ('N', 12),
    ('Q', 13),
    ('P', 14),
    ('S', 15),
    ('R', 16),
    ('T', 17),
    ('W', 18),
    ('V', 19),
    ('Y', 20)
])

def aa_integerMapping(peptideSeq):
    peptideArray = []
    for aa in peptideSeq:
        peptideArray.append(aa_idx[aa])
    return np.asarray(peptideArray)

def peptide_for_matrix(peptide):
    featureMatrix = np.empty((0, 43), int)
    for num in range(len(peptide)):
        featureMatrix = np.append(featureMatrix, [aa_integerMapping(peptide.iloc[num])], axis=0)
    return featureMatrix

df = pd.read_csv(sys.argv[1])
X_test =df.peptide
predScores = np.zeros((1, len(peptide_for_matrix(X_test))))
print X_test

model=load_model(os.path.join('model', 'hla_bi_lstm_model_20180601_dropout0.2_sigmoid_word2vec_size640.hdf5'))
predScores[0,:] =np.squeeze(model.predict(peptide_for_matrix(X_test)))

Y_pred = np.average(predScores, axis=0)
predicted_labels = [1 if score >= 0.5 else 0 for score in Y_pred]

if not os.path.exists('prediction_results'):
	os.makedirs('prediction_results')

with open(os.path.join('prediction_results', 'predictions.csv'), 'w') as f:
    f.write('Peptide_seq' + ',' + 'Predicted_Labels' + '\n')
    for i in range(len(Y_pred)):
        f.write(str(df['peptide'].iloc[i]) + ',' + str(predicted_labels[i]) + '\n')
f.close()

