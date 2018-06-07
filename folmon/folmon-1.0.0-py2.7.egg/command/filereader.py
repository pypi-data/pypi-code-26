from pandas import read_csv
from pandas import Series
from pandas import DataFrame
import pandas
import datetime
import os
import glob
import re

class CSVReader:
    def __init__(self, usage_location):
        self.path = usage_location
        self.df = DataFrame()

    def getBetweenDates(self, start_date, end_date):
        all_files = glob.glob(os.path.join(self.path,"*"))
        start_date = datetime.datetime.strptime(str(start_date), '%Y-%m-%d').date()
        end_date = datetime.datetime.strptime(str(end_date), '%Y-%m-%d').date()
        list_ = []
        series = None
        for f in all_files:
            file_date_match = re.search(r'\d{4}-\d{2}-\d{2}', f)
            if file_date_match:
                file_date = datetime.datetime.strptime(file_date_match.group(), '%Y-%m-%d').date()
                if (file_date >= start_date and file_date <= end_date):
                    if 'gz' in f:
                        series = read_csv(f,
                                        names=['date','folder', 'size'],
                                        header=None,
                                        index_col=0,
                                        parse_dates=[0],
                                        compression='gzip'
                                        )
                    else:
                        #print f
                        series = read_csv(f,
                                        names=['date','folder', 'size'],
                                        header=None,
                                        index_col=0,
                                        parse_dates=[0],
                                        )
                    list_.append(series)
        df = pandas.concat(list_)
        return df.sort_index()

    def getToday(self):
        start_date = end_date = datetime.date.today()
        return self.getBetweenDates(start_date, end_date)

    def getLastNDays(self,num_days):
        end_date = datetime.date.today()
        start_date = end_date - datetime.timedelta(days=num_days)
        return self.getBetweenDates(start_date, end_date)
    
    def getRecent(self):
        #FIXME: might not work if the user execute in 00.00 to 00:15 hours
        #For testing
        start_date=datetime.datetime.strptime('2018-05-10', '%Y-%m-%d').date()
        end_date=datetime.datetime.strptime('2018-05-10', '%Y-%m-%d').date()
        #start_date = end_date = datetime.date.today()
        today_df = self.getBetweenDates(start_date, end_date)
        return today_df.loc[today_df.index.max()]


if __name__ == "__main__":
    reader = CSVReader('/home/arun/Projects/bingoarun/folmon/sample-data')

    # Test getBetweenDates
    #start_date=datetime.datetime.strptime('2018-05-1', '%Y-%m-%d').date()
    #end_date=datetime.datetime.strptime('2018-05-10', '%Y-%m-%d').date()
    #print reader.getBetweenDates(start_date,end_date)

    # Test getToday()
    #print reader.getToday()

    #Test getLastNDays
    #print reader.getLastNDays(3)

    # Test getToday()
    #print reader.getRecent()