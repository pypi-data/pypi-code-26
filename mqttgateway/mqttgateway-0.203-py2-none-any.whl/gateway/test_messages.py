'''
Defines messages to test. Has to be updated depending on the interface being tested.
'''

# Syntax:  iscmd (bool), function (string) , gateway (string), location (string), device (string), source (string), action (string), arguments (dict)
_MESSAGES = [
    ( True, 'audiovideo', 'musiccast', 'office', 'undefined', 'undefined', 'POWER_ON', None),
    #( True, 'audiovideo', 'musiccast', 'office', 'undefined', 'undefined', 'SOURCE_CD', None),
    #( True, 'audiovideo', 'musiccast', 'office', 'undefined', 'undefined', 'CD_STOP', None),
    ( True, 'audiovideo', 'musiccast', 'office', 'undefined', 'undefined', 'SOURCE_NETRADIO', None),
    ( True, 'audiovideo', 'musiccast', 'office', 'undefined', 'undefined', 'NETRADIO_PRESET', {'preset':1}),

    ]