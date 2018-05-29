class SingletonMeta(type):
    _instances={}
    
    def __call__(cls,*args,**kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args,**kwargs)
        return cls._instances[cls]



class SingletonAbc(metaclass = SingletonMeta):
    """单例模式抽象基类.
    
    使用方法:
    
    class A(SingletonAbc):
        pass
    
    """
    pass