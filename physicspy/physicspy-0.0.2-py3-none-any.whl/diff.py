def df(x, f, h, **kwargs):
    
    if not kwargs:
        kwargs['points'] = 2
    
    points = kwargs['points']
    
    if points == 2:
        df = ( f(x + h) - f(x - h) ) / (2*h)
        
    if points == 4:
        df = ( f(x - 2*h) - 8*f(x - h) + 8*f(x + h) - f(x  + 2*h) ) / (12*h)
    
    return df

def d2f(x, f, h, **kwargs):
    
    d2f = (f(x + h) - 2*(f(x)) + f(x - h)) / (h**2)
    
    return d2f