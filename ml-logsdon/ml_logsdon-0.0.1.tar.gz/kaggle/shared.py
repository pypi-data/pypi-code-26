from sklearn.tree import DecisionTreeClassifier 

def getMissingCounts(df):
        list = [] #tupples
        for col in df.columns:
           list.append(tuple((col, df[col].isnull().sum())))
        list.sort(key=lambda v: v[1], reverse=True)
        return list
        
def removeMissingColumns(missingCounts, df):
    for column, count in missingCounts:
        if count > 0:
            df.drop(column=column, inplace=True)
            

def filterImportantColumns(y, X, keep=0.05):
    '''Reduce dimensionality based off of important columns
    data should already be encoded (DTC requires numeric data)
    '''
    model = DecisionTreeClassifier(max_depth=6)
    model.fit(X,y)
    important_columns = model.feature_importances_
    for index, col in enumerate(X.columns):
        if(important_columns[index] < keep):
            X.drop(col, inplace=True, axis=1)
    return X  

        
    
