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



class crawldata(object):

    def __init__(self):
	return
        
    def return_nonnulldf(self,df):
        df2 = df[[column for column in df if df[column].count() / len(df) >= 0.3]]
        print("List of dropped columns:")
        for c in df.columns:
            if c not in df2.columns:
                print(c)
        print('\n')
        return df2

    def feature_summary(self,df):
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



    def numerical_dist(self,df):
        df_num = df.select_dtypes(include = ['float64', 'int64'])
        df_num.hist(figsize=(16, 20), bins=50, xlabelsize=8, ylabelsize=8); # ; avoid having the matplot
        plt.show()
        return True

    def corr_analysis(self,df_num):
        for i in range(len(df_num.columns)):
            df_num_corr = df_num.corr()[df_num.columns[i]][:-1] # -1 because the latest row is SalePrice
            golden_features_list = df_num_corr[abs(df_num_corr) > 0.5].sort_values(ascending=False)
            print( df_num.columns[i]+" is strongly correlated values with  {}:\n{} ".format(len(golden_features_list), golden_features_list))
            print "\n"
        return True   

    def bivariate_analysis(self,df_num,interested_variable):
        for i in range(0, len(df_num.columns), 5):
            sns.pairplot(data=df_num,
                x_vars=df_num.columns[i:i+5],
                y_vars=[interested_variable])
        plt.show()
        return
    
