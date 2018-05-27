import pandas as pd
import numpy as np

import seaborn as sns
import matplotlib.pyplot as plt

from sklearn import *
from sklearn.metrics import make_scorer
from sklearn.grid_search import GridSearchCV

from scipy import *
from statsmodels import *
import xgboost as xgb




class Feature_Importance(object):

    def __init__(self,train_df,categorical,target):

        if (len(categorical)>0):
            for f in [categorical]:
                    print f
                    lbl = preprocessing.LabelEncoder()
                    lbl.fit(list(train_df[f].values)) 
                    train_df[f] = lbl.transform(list(train_df[f].values))

        train_y = train_df[target].values
        train_X = train_df.drop([target], axis=1)

        # Thanks to anokas for this #
        def xgb_r2_score(preds, dtrain):
            labels = dtrain.get_label()
            return 'r2', r2_score(labels, preds)

        xgb_params = {
            'eta': 0.05,
            'max_depth': 6,
            'subsample': 0.7,
            'colsample_bytree': 0.7,
            'objective': 'reg:linear',
            'silent': 1
        }
        dtrain = xgb.DMatrix(train_X, train_y, feature_names=train_X.columns.values)
        model = xgb.train(dict(xgb_params, silent=0), dtrain, num_boost_round=100, feval=xgb_r2_score, maximize=True)

        # plot the important features #
        fig, ax = plt.subplots(figsize=(12,18))
        xgb.plot_importance(model, max_num_features=50, height=0.8, ax=ax)
        plt.show()  
