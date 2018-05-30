__all__=['try_01']

class try_01(object):
    def __init__(self,f,*args):
        self.f=f
        self.f_param=args
    def run(self):
        return self.f(*self.f_param)