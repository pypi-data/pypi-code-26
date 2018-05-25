class Lazy(object):
  def __init__(_, func, *args = None, **kwargs = None):
    _.__func = func
    _.__args = args
    _.__kwargs = kwargs
  def __call__(_, *args, **kwargs):
    if isinstance(_.__func, types.LambdaType) and _.__func.__name__ == '<lambda>':
      return _.__func()
    return _.__func(*args, **kwargs)

a = Lazy(print, "abc")
a
