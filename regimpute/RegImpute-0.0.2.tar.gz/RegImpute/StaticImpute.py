import pandas as pd
import numpy as np
import warnings
import copy
from sklearn.preprocessing import Imputer
from sklearn.ensemble import RandomForestRegressor
import random; random.seed(3)
from sklearn.metrics import mean_squared_error


'''
Regression based imputation for Python.  
Author: Jeremy R. Jacobsen    
'''

class StaticImpute:
    def __init__(self,data,dataType,method,model=None,fillmethod="row_median",max_iter=100,mse=None):
        self.data = data 
        self.max_iter = max_iter
        self.mse = mse
        self.dataType = dataType
        self.method = method	
        self.model = model
        self.fillmethod = fillmethod
        self.verifyMethod(self.method,self.dataType)
        self.missing_positions=[]
        self.data_filled = []
        self.functionlist = {'regressionImpute': self.regressionImpute}

		
    def multi(self,imputed):
        dat = np.copy(self.data).astype(np.float64)
        missing_positions = np.argwhere(np.isnan(self.data))
        self.missing_positions = missing_positions
		

    def backFill(self,):
        '''
        This method fills in missing data with simple imputation schemes.  This data will be used later to boost
        prediction speed.
        '''
        dat = np.copy(self.data).astype(np.float64)
        missing_positions = np.argwhere(np.isnan(self.data))
        self.missing_positions = missing_positions

        if self.fillmethod=="col_median":
            mod = Imputer(missing_values=np.nan, strategy="median", axis=1)
            dat = mod.fit_transform(dat)
        if self.fillmethod=="row_median":
            mod = Imputer(missing_values=np.nan, strategy="median", axis=0)
            dat = mod.fit_transform(dat)
        return(dat)
	



    def verifyMethod(self,method,dataType):
        timeseries_methods = []
        static_methods = ['regressionImpute']
        if (dataType=='timeseries') & (method in timeseries_methods):
            return(None)
        if (dataType=='static') & (method in static_methods):
            return(None)
        else:
            raise Exception('Method['+method+'] is undefined or data_type['+dataType+'] are incompatible!')




    def impute(self,data=None):
        print("Imputing...")
        if data is None: 
            data = self.data
        imputed=None

        #If any rows or columns are missing entirely, then remove those until after imputation
        #Update MSE and break loop if MSE<=alpha
   
        for i in range(self.max_iter):
            imputed,previous = self.functionlist[self.method](self.data,imputed)
            if (previous is not None):
                delta = mean_squared_error(imputed.flatten(),previous.flatten())
                print("MSE on iteration "+str(i)+": "+str(delta))
                if (self.mse is not None):
                    if delta<=self.mse:
                        break
        print("Imputation Complete!")
        return(imputed)

	


	


	

    #---------------------------------------REGRESSION IMPUTATION-----------------------------------------------#
	
    def regressionImpute(self,data,imputed):
        if self.dataType!='static':
            warnings.warn("Running static imputation on dataset not specified to be static!")
        if self.model==None:
            model=RandomForestRegressor(n_estimators=50, criterion='mse')	
        else:
            model=self.model
		
        if imputed is None:
            previous = None
            self.data_filled = self.backFill()
            datacopy = np.copy(data)
        else:
            previous = imputed.copy()
            self.data_filled = imputed
            datacopy = np.copy(data)
			
		
        def returnTrainTargetTest(col,datacopy):
            #Indices @ current column, only where values aren't missing
            present_indices = np.where(~np.isnan(datacopy[:,col]))[0] 
            #Only rows where value is present at current column.  All columns except for current.
            train = np.delete(self.data_filled, col, axis=1)[present_indices]
            #Current column, only indices where values were present in original data
            target = datacopy[present_indices,col].reshape(-1,1)
            #Indices @ current column, only where values are missing		
            test_indices = np.where(np.isnan(datacopy[:,col]))[0]
            test = np.delete(self.data_filled, col, axis=1)[test_indices]
            return (train,target,test,test_indices,present_indices)

	
        for col in range(data.shape[1]):
            #continue if there aren't any missing values to impute for current column
            if len(np.where(np.isnan(datacopy[:,col]))[0])==0:
                continue
            else:
                train,target,test,test_indices,present_indices = returnTrainTargetTest(col,datacopy)
                model.fit(train,target)
                datacopy[test_indices,col] = model.predict(test).reshape(1,-1)
        return (datacopy,previous)





 
		
		




			
		
		
		
	










