from rest_framework import serializers

import arrow

class UnixEpochTimeField(serializers.TimeField):

    def __init__(self, **kwargs):
        if kwargs.get('allow_null') == None:
            kwargs['allow_null'] = True
        super(UnixEpochTimeField, self).__init__(**kwargs)
        
    
    def to_representation(self, value):
        '''value is a django TimeField, convert that to number of seconds since midnight.
        we assume all times in UTC.'''
        
        if value == None:
            response = None
        else:
            response = arrow.get(value).timestamp
        return response

    def to_internal_value(self, data):
        if data == None:
            response = None
        else:
            response = arrow.get(data).datetime
        return response

class UnixEpochTimeFieldHuman(serializers.SerializerMethodField):
    def __init__(self, source_name, *arg, **kwargs):
        self.source_name = source_name
        super(UnixEpochTimeFieldHuman, self).__init__(*arg, **kwargs)
        
    
    def to_representation(self, value):
        '''value is a django TimeField'''
        atime = getattr(value, self.source_name) # get the value of interest!
        
        if atime == None:
            response = None
        else:
            response = arrow.get(atime).format('HH:mm:ss') # 24 hour formatted human readable time.  It is in UTC
        return response






    