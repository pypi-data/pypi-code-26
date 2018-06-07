import prettytable 
from StringIO import StringIO
from core import CoreAnalysis

class Presentation:
    def __init__(self, path):
        self.ca = CoreAnalysis(path)
        
    def getRecentStatus(self):
        df = self.ca.getCurrentUsage()
        df = df.rename(columns={'size':'size(MB)'})
        df = df.round(3)
        output = StringIO()
        df.to_csv(output)
        output.seek(0)
        pt = prettytable.from_csv(output)
        print pt
    
    def getBetweenDates(self,start_date,end_date,folder):
        df = self.ca.getBetweenDates(start_date,end_date,folder)
        #print df.columns[2]
        #df.columns[2] = int(df.columns[2])/(1024*1024)

        #df = df.rename(columns={'size':'size(MB)'})
        df = df.round(3)
        output = StringIO()
        df.to_csv(output)
        output.seek(0)
        pt = prettytable.from_csv(output)
        print pt

        

if __name__ == "__main__":
    
    presentation_obj = Presentation('/home/arun/Projects/bingoarun/folmon/sample-data')
    #presentation_obj.getRecentStatus()
    presentation_obj.getBetweenDates('2018-05-05','2018-05-07',"/log/fruit")