import sanitize

class AthleteList(list):
    def __init__(self,name,dob=None,times=[]):
        list.__init__([])
        self.name=name
        self.dob=dob
        self.extend(times)
        
    def top3(self):
        return sorted(set([sanitize.sanitize(t) for t in self]))[0:3]
