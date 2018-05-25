import jsonpickle
import datetime


class BaseParameter():

    def __init__(self, name):
        self.name = name

    def __get__(self, obj, owner):
        return getattr(obj, self.name, None)

    def __set__(self, obj, value):
        setattr(obj, self.name, value)


def acceptsValues(values):
    def decorator(func):
        def wrapper(*args, **kwwargs):
            if isinstance(values, (list, )):
                if args[1] in values:
                    return func(*args, **kwargs)
                else:
                    raise ValueError(f'Must be one of {values}')
            else:
                raise TypeError(f'Valid values musst be of type {type(list)}')
        return wrapper
    return decorator


def acceptsWeekday(weekday):
    def decorator(func):
        def wrapper(*args, **kwargs):
            if isinstance(args[1], datetime.date):
                date = args[1]
                args[1] = datetime.datetime.strftime(date, '%Y-%m-%d')
            else:
                date = datetime.datetime.strptime(args[1], '%Y-%m-%d').date()
            if date.weekday() != weekday:
                raise ValueError(f'Musst be day {weekday}, {date.weekday()} was given')
            return func(*args, **kwargs)
        return wrapper
    return decorator


class MethodParams():
    
    def __init__(self, fixed, needed, optional=None):
        self._fixed = fixed
        self._needed = needed
        self._optional = optional  
        self.reset()

    @property
    def fixed(self):
        return self._fixed

    @property
    def needed(self):
        return self._needed

    @property
    def optional(self):
        return self._optional

    def get(self):
        """Get parameters
        
        Builds dict from parameters
        
        Returns
        -------
        dict
            Parameters for API call
        """
        return jsonpickle.decode(jsonpickle.encode(self, unpicklable=False))

    def check_needed(self):
        """Check needed
        
        Checks if all needed parameters are present.
        
        Raises
        ------
        ValueError
            Error if needed parameter is not given.
        """
        for need in self.needed:
            if getattr(self, need, None) == None:
                raise ValueError(f'{need} can not be {type(None)}')


    def reset(self):
        """Reset parameters

        Reset the optional parameters
        """
        if self.optional is not None:
            for value in self.optional:
                setattr(self, value, None)
        for value in self.needed:
            setattr(self, value, getattr(self, value, None))
        for item,value in self.fixed.items():
            setattr(self, item, value)
        
    def __getstate__(self):
        state = self.__dict__.copy()
        for attr in ['_fixed','_needed','_optional']:
            del state[attr]
        return state


class BaseMethod():

    def __init__(self, client, endpoint, *args, **kwargs):
        self._endpoint = endpoint
        self._client = client

    def __repr__(self):
        return f'<metrics.tools Method [{self.params.query}]>'

    def get(self):
        """Get result
        
        Run API call for method
        
        Returns
        -------
        ClientResponse
            metrics.tools response object
        """
        self.params.check_needed()
        self._client.params = self.params.get()
        self.params.reset()
        return self._client.get(self._endpoint)


class Paginatable(BaseMethod):

    def get(self, offset=0, limit=10):
        """Get result by offset and limit
        
        Run API call for method
        
        Parameters
        ----------
        offset : {number}, optional
            Paginationoffset (the default is 0)
        limit : {number}, optional
            Resultlimit, default 10, maximum 1000 (the default is 10)
        
        Returns
        -------
        ClientResponse
            metrics.tools response object
        """
        self.params.check_needed()
        self._client.params = {**self.params.get(), **{'offset':offset,'limit':limit}}
        self.params.reset()
        return self._client.get(self._endpoint)

    def all(self, **kwargs):
        """Get all results
        
        Run paginated API call for method
        
        Returns
        -------
        ClientResponse
            metrics.tools response object
        """
        num = kwargs.get('num', float('inf'))
        limit = num if num < 1000 else 1000
        offset = 0
        iterations = 1
        self.params.check_needed()
        while True:
            if iterations * limit <= offset or num <= offset:
                self.params.reset()
                break
            self._client.params = {**self.params.get(), **{'offset':offset,'limit':limit}}
            response = self._client.get(self._endpoint)
            if response.result == 'success' and len(response) > 0: #result present, no error
                if offset == 0: #first run
                    if hasattr(response, 'n_all'): #calc interations for all results
                        x = divmod(response.n_all, limit)
                        iterations = x[0] + 1 if x[1] > 0 else x[0]
                    result = response
                else:
                    result.__dict__['values'].extend(response.__dict__['values'])
                if iterations == 1: break
            else:
                result = response
                self.params.reset()
                break
            offset += limit
        return result

    def take(self, num):
        """Get first n results by num
        
        Run paginated API call for method for first n results
        
        Returns
        -------
        ClientResponse
            metrics.tools response object
        """
        return self.all(num=num)


class AcceptsOrderColumn():

    def orderby(self, column, direction='desc'):
        """Sort result
        
        Sort result by column and direction
        
        Parameters
        ----------
        column : {string}
            Sort by column, default: traffic, possible values: position, searchvolume, traffic
        direction : {str}, optional
            Sortierungsrichtung, default: desc, mögliche Werte: asc, desc (the default is 'desc')
        
        Returns
        -------
        self
        """
        self.params.order_column = column
        self.params.order_direction = direction
        return self


class AcceptsDateFilter():

    @acceptsWeekday(0)
    def from_(self, date):
        """Set date
        
        Filters API call for specific date
        
        Parameters
        ----------
        date : {string or datetime.date}
            - needs to be monday
            - string format 'yyyy-mm-dd'
        
        Returns
        -------
        self
        """
        self.params.date = date
        return self

class AcceptsKeywordFilter():

    def for_keyword(self, keyword):
        """Set Keyword
        
        Filter API call for given keyword.

        Parameters
        ----------
        keyword : {string}
            Keyword to filter for
        
        Returns
        -------
        self
        """
        self.params.keyword = keyword
        return self

if __name__ == '__main__':
    pass