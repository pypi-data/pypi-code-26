import pandas as pd
import numpy as np

import seaborn as sns
import matplotlib.pyplot as plt

from sklearn import *
from sklearn.metrics import make_scorer
from sklearn.grid_search import GridSearchCV

from scipy import *
from statsmodels import *

class Model_Factory(object):

    def __init__(self):



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

        class GetBestModel(object):

            def __init__(self, models, params):

                if not set(models.keys()).issubset(set(params.keys())):
                    missing_params = list(set(models.keys()) - set(params.keys()))
                    raise ValueError("Some estimators are missing parameters: %s" % missing_params)
                self.models = models
                self.params = params
                self.keys = models.keys()
                self.grid_searches = {}

            def fit(self, X, y, cv=3, n_jobs=1, verbose=1, scoring='1', refit=True):
                for key in self.keys:
                    model = self.models[key]
                    params = self.params[key]
                    gs = GridSearchCV(model, params, cv=cv, n_jobs=n_jobs, 
                                      verbose=False, scoring=scoring, refit=refit)
                    gs.fit(X,y)
                    self.grid_searches[key] = gs    

            def score_summary(self, sort_by='mean_score'):
                def row(key, scores, params):
                    d = {
                         'estimator': key,
                         'min_score': min(scores),
                         'max_score': max(scores),
                         'mean_score': np.mean(scores),
                         'std_score': np.std(scores),
                    }
                    return pd.Series(dict(params.items() + d.items()))

                rows = [row(k, gsc.cv_validation_scores, gsc.parameters) 
                             for k in self.keys
                             for gsc in self.grid_searches[k].grid_scores_]

                df = pd.concat(rows, axis=1).T.sort_values(sort_by, ascending=False)  
                columns = ['estimator', 'min_score', 'mean_score', 'max_score', 'std_score']
                columns = columns + [c for c in df.columns if c not in columns]

                return df[columns]  


        class Crawl_Data(object):

            def __init__(self):


                def return_Non_Null_df(self,df):
                    df2 = df[[column for column in df if df[column].count() / len(df) >= 0.3]]
                    print("List of dropped columns:")
                    for c in df.columns:
                        if c not in df2.columns:
                            print(c)
                    print('\n')
                    return df2

                def FeatureTypes(self,df):
                    df_train=df
                    counts = [[], [], []]
                    cols =  df_train.columns 
                    for c in cols:
                        typ = df_train[c].dtype
                        uniq = len(np.unique(df_train[c]))
                        if uniq == 1: counts[0].append(c)
                        elif uniq == 2 and typ == np.int64: counts[1].append(c)
                        else: counts[2].append(c)

                    print('Constant features: {} Binary features: {} Categorical features: {}\n'.format(*[len(c) for c in counts]))

                    print('Constant features:', counts[0])
                    print('Numerical features:', counts[1])
                    print('Categorical features:', counts[2])



                def Numerical_Data_Distribution(self,df):
                    df_num = df.select_dtypes(include = ['float64', 'int64'])
                    df_num.hist(figsize=(16, 20), bins=50, xlabelsize=8, ylabelsize=8); # ; avoid having the matplot
                    plt.show()
                    return True

                def Correlation_Analysis(self,df_num):


                    for i in range(len(df_num.columns)):
                        df_num_corr = df_num.corr()[df_num.columns[i]][:-1] # -1 because the latest row is SalePrice
                        golden_features_list = df_num_corr[abs(df_num_corr) > 0.5].sort_values(ascending=False)
                        print( df_num.columns[i]+" is strongly correlated values with  {}:\n{} ".format(len(golden_features_list), golden_features_list))
                        print "\n"
                    return True   

                def Bivariate_Analysis(self,df_num,interested_variable):
                    for i in range(0, len(df_num.columns), 5):
                        sns.pairplot(data=df_num,
                                    x_vars=df_num.columns[i:i+5],
                                    y_vars=[interested_variable])
                        plt.show()

