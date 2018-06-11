"""
    The commands understood by the Pi Stack PCB
    Philip Basford
    October 2017
"""
CMD_RESPONSE_OK = 0x00
CMD_RESPONSE_ERROR = 0x01


# Admin commands
CMD_GET_SW_VERSION = 0x02
CMD_GET_HW_VERSION = 0x03
CMD_LEDS_ON = 0x04
CMD_LEDS_OFF = 0x05
CMD_DEBUG_LED = 0x06
CMD_SET_ID_PREFIX = 0x07
CMD_GET_ID_PREFIX = 0x08
CMD_GET_ID = 0x09

#Status commands
CMD_GET_VIN = 0x0A
CMD_GET_CIN = 0x0B
CMD_GET_5V = 0x0C
CMD_GET_PI_V = 0x0D
CMD_GET_PI_C = 0x0E
CMD_GET_PI_HBT = 0x0F
CMD_GET_PI_POWERED = 0x10

# Control commands
CMD_PI_ON = 0x11
CMD_PI_OFF = 0x12
CMD_PI_FORCE_OFF = 0x13

# Timer commands
CMD_GET_HBT_TIME = 0x14
CMD_SET_HBT_TIME = 0x15
CMD_GET_HBT_DELAY = 0x16
CMD_SET_HBT_DELAY = 0x17
CMD_GET_OFF_DELAY = 0x18
CMD_SET_OFF_DELAY = 0x19
CMD_GET_SIG_OFF_DELAY = 0x1A
CMD_SET_SIG_OFF_DELAY = 0x1B

#Error log commands
CMD_GET_ERROR_BUFFER = 0x1C
CMD_CLEAR_ERROR_BUFFER = 0x1D
CMD_GET_ERROR_COUNT = 0x1E
CMD_CLEAR_ERROR_COUNT = 0x1F
CMD_GET_ERROR_POINTER = 0x20

#Testing commands
CMD_SEND_SIG = 0x21


# Config commands
CMD_GET_PI_ON_STARTUP = 0x22
CMD_SET_PI_ON_STARTUP = 0x23
CMD_GET_SIG_WIDTH = 0x24
CMD_SET_SIG_WIDTH = 0x25

# Power commands
CMD_GET_POWER = 0x26
CMD_GET_5V_POWER = 0x27
CMD_GET_PI_POWER = 0x28

# Boot count
CMD_GET_BOOT_COUNT = 0x29

# Command Summary
NO_CMDS = 42

# Command indexes
CMD_INDEX = 0 # Byte that contains the command
ADDRESS_INDEX = 1 # Byte the contains the address the CMD is sent to
LENGTH_INDEX = 2 # Byte that contains the length of the command
DATA_START_INDEX = 3 #First byte that contains data

CMD_MIN_LENGTH = 3 # Minimum length = cmd, address, length,  THIS EXCLUDES CRC
CMD_RESP_MIN_LENGTH = 3 # Minimum length = cmd, address, length,  THIS EXCLUDES CRC
CMD_MASTER_ADDRESS = 0xFF

# Command Lengths
CMD_MIN_LENGTHS = [
    0,  #Response so not valid as an input
    0,  #Response so not valid as an input
    CMD_MIN_LENGTH,  #get sw version: cmd, addr, lngth
    CMD_MIN_LENGTH,  #get hw version: cmd, addr, lngth
    CMD_MIN_LENGTH,  #debug leds on: cmd, addr, lngth
    CMD_MIN_LENGTH,  #debug leds off: cmd, addr, lngth
    CMD_MIN_LENGTH + 3, #rgb led: cmr, addr, legnth, r, g, b
    CMD_MIN_LENGTH + 1,  #Set prefix: cmd, addr, lngth, prefix
    CMD_MIN_LENGTH,  #Get prefix: cmd, addr, lngth
    CMD_MIN_LENGTH,  #Get Id: cmd, addr, lngth
    CMD_MIN_LENGTH,  #Get Vin: cmd, addr, lngth
    CMD_MIN_LENGTH,  #Get CIN: cmd, addr, lngth
    CMD_MIN_LENGTH,  #Get 5v: cmd, addr, lngth
    CMD_MIN_LENGTH + 1,  #Get pi 5v: cmd, addr, lngth, id
    CMD_MIN_LENGTH + 1,  #Get pi current: cmd, addr, lngth, id
    CMD_MIN_LENGTH + 1,  #Get pi  heartbeat: cmd, addr, lngth, id
    CMD_MIN_LENGTH + 1,  #Get pi status: cmd, addr, lngth, id
    CMD_MIN_LENGTH + 1,  #Pi on : cmd, addr, lngth, id
    CMD_MIN_LENGTH + 1,  #Pi off : cmd, addr, lngth, id
    CMD_MIN_LENGTH + 1, #Pi force off : cmd, addr, lngth, id
    CMD_MIN_LENGTH + 1,       #Get HBT Time : cmd, addr, lngth, id
    CMD_MIN_LENGTH + 2,   #Set HBT Time: cmd, add, lngth, id, time
    CMD_MIN_LENGTH + 1,       #Get HBT delay: cmd, addr, length, id
    CMD_MIN_LENGTH + 2,   #Set HBT delay: cmd, addr, length, id, time
    CMD_MIN_LENGTH + 1,       #Get off delay: cmd, addr, lngth, id
    CMD_MIN_LENGTH + 2,   #set off delay: cmd, addr, lngth, id, time
    CMD_MIN_LENGTH + 1,       #get sig delay: cmd, addr, lngth, id
    CMD_MIN_LENGTH + 2,   #set sig delay: cmd, addr, lngth, id, time
    CMD_MIN_LENGTH,       #get error buffer: cmd, addr, length
    CMD_MIN_LENGTH,       #clear error buffer: cmd, addr, length
    CMD_MIN_LENGTH,       #get error count: cmd, addr, length
    CMD_MIN_LENGTH,        #clear error count: cmd, addr, length
    CMD_MIN_LENGTH,         #get error pointer: cmd, addr, lengtha
    CMD_MIN_LENGTH + 1,     #Send signal: cmd, addr, lngth, id
    CMD_MIN_LENGTH + 1,       #CMD_GET_PI_ON_STARTUP: cmd, addr, lngth, id
    CMD_MIN_LENGTH + 2,       #CMD_SET_PI_ON_STARTUP: cmd, addr, lngth, id, value
    CMD_MIN_LENGTH + 1,       #CMD_GET_SIG_WIDTH: cmd, addr, lngth, id
    CMD_MIN_LENGTH + 2,       #CMD_SET_SIG_WIDTH: cmd, addr, lngth, id, value
    CMD_MIN_LENGTH,         #CMD_GET_POWER: cmd, addr, length
    CMD_MIN_LENGTH,        #CMD_GET_5V_POWER: cmd, addr, length
    CMD_MIN_LENGTH + 1,       #CMD_GET_PI_POWER: cmd, addr, lngth, id
    CMD_MIN_LENGTH,           #CMD_GET_BOOT_COUNT, cmd, addr, lngth
]

RESPONSE_LENGTHS = [
    CMD_RESP_MIN_LENGTH,  #ok: cmd, addr, length
    CMD_RESP_MIN_LENGTH + 1,  #err: cmd, addr, lrngth, err
    CMD_RESP_MIN_LENGTH + 1,  #get sw version: cmd, addr, lngth, version,
    CMD_RESP_MIN_LENGTH + 1,  #get hw version: cmd, addr, lngth, version,
    CMD_RESP_MIN_LENGTH,  #debug leds on: cmd, addr, lngth,
    CMD_RESP_MIN_LENGTH,  #debug leds off: cmd, addr, lngth,
    CMD_RESP_MIN_LENGTH,  #rgb led off: cmd, addr, lngth,
    CMD_RESP_MIN_LENGTH,  #Set prefix: cmd, addr, lngth,
    CMD_RESP_MIN_LENGTH + 1,  #Get prefix: cmd, addr, lngth, prefix,
    CMD_RESP_MIN_LENGTH + 1,  #Get Id: cmd, addr, lngth, id,
    CMD_RESP_MIN_LENGTH + 2,  #Get Vin: cmd, addr, lngth, vinH, vinL,
    CMD_RESP_MIN_LENGTH + 2,  #Get CIN: cmd, addr, lngth, CinH, CinL,
    CMD_RESP_MIN_LENGTH + 2,  #Get 5v: cmd, addr, lngth, 5vH, 5vL,
    CMD_RESP_MIN_LENGTH + 2,  #Get pi 5v: cmd, addr, lngth, 5vH, 5vL,
    CMD_RESP_MIN_LENGTH + 2,  #Get pi current: cmd, addr, lngth, CH, CL,
    CMD_RESP_MIN_LENGTH + 1,  #Get pi  heartbeat: cmd, addr, lngth, status,
    CMD_RESP_MIN_LENGTH + 1,  #Get pi status: cmd, addr, lngth, status,
    CMD_RESP_MIN_LENGTH,  #Pi  on : cmd, addr, lngth,
    CMD_RESP_MIN_LENGTH,  #Pi  off : cmd, addr, lngth,
    CMD_RESP_MIN_LENGTH,  #Pi  force off : cmd, addr, lngth,
    CMD_RESP_MIN_LENGTH + 1,       #Get HBT Time : cmd, addr, lngth, , time
    CMD_RESP_MIN_LENGTH,   #Set HBT Time: cmd, add, lngth
    CMD_RESP_MIN_LENGTH + 1,       #Get HBT delay: cmd, addr, length, time
    CMD_RESP_MIN_LENGTH,   #Set HBT delay: cmd, addr, length
    CMD_RESP_MIN_LENGTH + 1,       #Get off delay: cmd, addr, lngth, time
    CMD_RESP_MIN_LENGTH,   #set off delay: cmd, addr, lngth
    CMD_RESP_MIN_LENGTH + 1,       #get sig delay: cmd, addr, lngth, time
    CMD_RESP_MIN_LENGTH,   #set sig delay: cmd, addr, lngth
    CMD_RESP_MIN_LENGTH + 1, #get error buf: cmd,addr,lngth,error maybe longer
    CMD_RESP_MIN_LENGTH,  #clear error buffer: cmd, addr, length
    CMD_RESP_MIN_LENGTH + 2, #get error count: cmd, addr, length, cnt_h, cnt_l
    CMD_RESP_MIN_LENGTH, #clear error coutn: cmd, addr, length
    CMD_RESP_MIN_LENGTH + 1, #get error pointer: cmd, addr, length, pointer
    CMD_RESP_MIN_LENGTH, #send signal: cmd, addr, length
    CMD_RESP_MIN_LENGTH +1,  #CMD_GET_PI_ON_STARTUP: cmd, addr, lngth, status
    CMD_RESP_MIN_LENGTH, #CMD_SET_PI_ON_STARTUP: cmd, addr, lngth
    CMD_RESP_MIN_LENGTH +1,  #CMD_GET_SIG_WIDTH: cmd, addr, lngth, status
    CMD_RESP_MIN_LENGTH, #CMD_SET_SIG_WIDTH: cmd, addr, lngth
    CMD_RESP_MIN_LENGTH + 4, #CMD_GET_POWER: cmd, addr, lngth, value4, value3, value2, value1
    CMD_RESP_MIN_LENGTH + 4, #CMD_GET_5V_POWER: cmd, addr, lngth, value4, value3, value2, value1
    CMD_RESP_MIN_LENGTH + 4, #CMD_GET_PI_POWER: cmd, addr, lngth, value4, value3, value2, value1
    CMD_RESP_MIN_LENGTH +2, #CMD_GET_BOOT_COUNT: cmd, addr, lngth, value2, value1
]


