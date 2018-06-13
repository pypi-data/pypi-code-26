def loggable(func_name):
    def wrapper(*args,**kwargs):
        # init logger

        return func_name(*args,**kwargs)
    return wrapper