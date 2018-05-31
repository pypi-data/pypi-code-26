import json
import traceback

def traceback_to_str(exception = None):
    '''Simple convience function that converts the full stack trace to a string'''
    traceback_str = repr(traceback.format_exc())
    return traceback_str

class GenericResponse(dict):
    '''Provide structure in basic responses instead of passing around a bunch of dictionaries and tuples.
    Information is loaded in upon initialization.  While there are no direct checks, would be odd if your 
    response values changed.
    '''
    
    ALLOWED_KEYS = ('success', 'data', 
                    'status_code', 'status_message',
                    'error_code', 'error_message',
                    'warning_code', 'warning_message',
                    'exception', 'exception_str'
                    )
    def __init__(self, 
                **kwargs
                 ):
#         for key in self.ALLOWED_KEYS: # set the default value if neeeded
#             kwargs[key] = kwargs.get(key, None)
            
        super(GenericResponse, self).__init__(**kwargs)
        
        if self.exception is not None:
            self.exception_str = traceback_to_str(self.exception)
        
#         self.success = success  # typically a True/False
#         
#         self.status_code = status_code        # an integer code for the status
#         self.status_message = status_message  # correspoding human message
#         
#         self.data = data  # information that is passed back and forth from the response, if needed
#             
#         self.error_code = error_code # an integer code for the error if applicable
#         self.error_message = error_message # correspoding human message for error
#         
#         
#         self.exception = exception  # a caught Exception, assumptions are later used to allow for proper JSON conversion
#         
#         self.warning_code = warning_code # an integer code for warning
#         self.warning_message = warning_message # corresponding human message for the warning
#     
    def __iter__(self):
        '''Allow for following use case:
        success, response = GenericResponse(success = True, data = 'ha')
        
        Note that it will ALWAYS be (success, self) beign returned 
        This cannot change without changing everything!
        '''
        for i in (self.success, self):
            yield i
    
    
    def __getattr__(self, attr):
        if attr in self.ALLOWED_KEYS:
            return self.get(attr)
         
        raise AttributeError("GenericResponse object has no attribute '{attr}'".format(attr = attr))
    
    
    def get_response(self):
        '''Method version of response property'''
        return self.response
    
    @property
    def response(self):
        '''a dictionary of only the relevant information.
        all responses will always have:  success, data as keys
        all other keys are optional and not included if None
        '''
        
        # always have the following keys
        response = dict(
            success = self.success,
            data = self.data,
            )
        
        for key in self.ALLOWED_KEYS():
            if key in ('success', 'data', 'exception_str'):
                continue
            elif self[key] is None:
                continue
            elif key == 'exception' and self.exception_str is not None:
                response[key] = self.exception_str
            else:
                response[key] = self['key']

        return response

    
    def to_json(self):
        '''Convience function to get the json formatted version'''
        return self.json
    
    @property
    def json(self):
        '''Convert response to proper json.'''
        return json.dumps(self.response)
    
    def raise_exception(self):
        '''Attempt to raise an exception if there was one.  Note that
        raise, will raise the most recent Exception and not necessarily the one
        that is stored here.'''
        if self.exception is not None:
            print(self.exception_str)
            raise self.exception
        
    
#     def __repr__(self):
#         return self.response

def main():
    try:
        raise ValueError('haasdfasdf')
    
    except Exception as e:
        
        
        
        gr = GenericResponse(exception = e)
        
        print(gr.success)
#         print(gr.random)
#         gr = GenericResponse(success = False, data = 'test', exception = e)
    try:
        raise TypeError('ha')
    except:
        pass
    
    
    success, gr = gr
#     
    print(success, gr)
    
    print(gr.raise_exception())

if __name__ == '__main__':
    main()