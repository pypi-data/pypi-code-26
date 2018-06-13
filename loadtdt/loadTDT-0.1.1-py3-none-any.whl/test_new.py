
class AbstractClass():
    def __new__(cls, *args, **kwargs):
        instance = super(AbstractClass, cls).__new__(cls)
        instance.__init__(*args, **kwargs)
        value = instance.compute()
        return value
 
    def __init__(self, a, b):
        print("Initializing Instance", a, b)
        self.a = a
        self.b = b
        
    def compute(self):
        return self.a + self.b


print(AbstractClass(1,2))
print(AbstractClass(5,2))
print(AbstractClass(1,2))

class loadTDT():
    def __new__(cls, *args, **kwargs):
        instance = super(loadTDT, cls).__new__(cls)
        instance.__init__(*args, **kwargs)
        return instance.load()
 
    def __init__(self, a, b):
        pass
        
    def load(self):
        data = 'insert data here'
        return data
