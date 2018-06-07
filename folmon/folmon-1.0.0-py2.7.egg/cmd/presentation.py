import prettytable 
from StringIO import StringIO
from core import CoreAnalysis

class Presentation:
    def __init__(self, path):
        self.ca = CoreAnalysis(path)
        
    def getRecentStatus(self):
        df = self.ca.getCurrentUsage()
        df['size'] = df['size']/(1024*1024)
        df = df.rename(columns={'size':'size(MB)'})
        df = df.round(3)
        output = StringIO()
        df.to_csv(output)
        output.seek(0)
        pt = prettytable.from_csv(output)
        print pt

        

if __name__ == "__main__":
    
    presentation_obj = Presentation('/home/arun/Projects/bingoarun/folmon/sample-data')
    presentation_obj.getRecentStatus()