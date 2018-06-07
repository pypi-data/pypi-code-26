# series = read_csv('usage/usage-2018-05-10.csv',
#             names=['date','folder','size'],
#             header=0,
#             index_col=0,
#             parse_dates=[0])
# #print series.tail(10)
# #print(series['2018-05-10 23-45'])
# df = DataFrame(series)
# #print df.loc['2018-05-10 23:40:00':'2018-05-10 23:50:00']
# df_recent = df.loc[datetime.datetime(2018, 5, 10,23,40,0):datetime.datetime(2018, 5, 10,23,50,0)]
# print df_recent
# total=int(df_recent.loc[df_recent['folder'] == '/log','size'].item())
# df_recent['percentage'] = (df_recent['size']/total)*100
# print df_recent

from filereader import CSVReader

class CoreAnalysis:

    def __init__(self,path):
        self.reader = CSVReader(path)

    def getCurrentUsage(self):
        df_recent = self.reader.getRecent()
        total=int(df_recent.loc[df_recent['folder'] == '/log','size'].item())
        df_recent['percentage'] = (df_recent['size']/total)*100
        return df_recent

if __name__ == "__main__":
    #reader = CSVReader('/home/arun/Projects/bingoarun/folmon/sample-data')
    ca = CoreAnalysis('/home/arun/Projects/bingoarun/folmon/sample-data')
    print ca.getCurrentUsage()
    
