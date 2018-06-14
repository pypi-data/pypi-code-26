# import necessary packages
import pandas as pd
import numpy as np
from sklearn.preprocessing import Imputer
from sklearn.preprocessing import LabelEncoder, OneHotEncoder

# Clean Missing Data with a mesh of pandas' fillna and sklearn's Imputer
def clean_missing(dataframe, column, clean_type="mean"):
	clean_types = ["zero", "mean", "mode", "most_frequent"]
	if clean_type not in clean_types:
		raise ValueError("clean_type not one of available types (['zero', 'mean', 'mode', 'most_frequent'])")
	else:
		# fillna
		if clean_type == "zero":
			dataframe[column] = dataframe[column].fillna(0)
		# imputer
		else:
			imputer = Imputer(missing_values='NaN', strategy=clean_type, axis=0)
			imputer = imputer.fit(dataframe[[column]])
			dataframe[column] = imputer.transform(dataframe[[column]])

		return dataframe


# Encoding categorical features
def convert_categorical(dataframe, column, target_column):
	# One hot encode categories and add back individual columns to dataframe
	dataframe = pd.concat([dataframe, pd.get_dummies(dataframe[column], prefix=column)], axis=1)
	# Drop original column
	dataframe.drop([column], axis=1, inplace=True)
	# Moving target back to the end. Create second dataframe for target
	dataframe_two = dataframe[target_column]
	# Delete target column from original dataframe
	dataframe.drop([target_column], axis=1, inplace=True)
	# Add target column back to end of dataframe
	dataframe = pd.concat([dataframe, dataframe_two], axis=1)

	return dataframe