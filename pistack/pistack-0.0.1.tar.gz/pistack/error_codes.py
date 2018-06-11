"""
    Pi Stack error conversion
    Philip Basford
    08/05/2018
"""

from pistack.errors import InvalidErrorCode
# Sucess statuses
_SUCCESS = 0x00
_ERR_CMD_NO_ID_MATCH = 0x02

_BOOT_OK = 0x0F
# Command Processing
_ERR_CMD_TOO_SHORT = 0x10
_ERR_CMD_CRC_FAIL = 0x11
_ERR_CMD_UNKNOWN = 0x12
_ERR_CMD_WRONG_LENGTH = 0x13    #Not enough args for command given
_ERR_INVALID_PI_ID = 0x14
_ERR_CMD_NOT_IMPLEMENTED = 0x15

# Comms***********************************************************************/
_ERR_COMMS_NOT_READABLE = 0x20
_ERR_COMMS_TOO_LONG = 0x21
_ERR_COMMS_BUFFER_LENGTH_MISMATCH = 0x22
_ERR_COMMS_BUFFER_NOT_LONG_ENGOUGH = 0x23    #cannot fit response in buffer

# Error handling**************************************************************/
_ERR_BUFFER_TOO_SMALL_FOR_ERRORS = 0x30

# Storage**************************************************************/
_ERR_CONFIG_CRC_FAILURE = 0x40
_ERR_ERRORS_CRC_FAILURE = 0x41
_ERR_IAP_ERASE_PREPARE_FAIL = 0x42
_ERR_IAP_ERASE_FAIL = 0x43
_ERR_IAP_WRITE_PREPARE_FAIL = 0x44
_ERR_IAP_WRITE_FAIL = 0x45
_ERR_IAP_COMPARE_FAIL = 0x46
_ERR_IAP_BLANK_CHECK_FAIL = 0x47
_ERR_IAP_COMPARE_FAILURE = 0x48

_MAX_NON_STORED_ERROR = 0x0E    #The highest status code which doesn't represent an error

_ERRORS = {}
_ERRORS[_SUCCESS] = "Success / Not used yet"
_ERRORS[_ERR_CMD_NO_ID_MATCH] = "Not the ID of this pi stack"
_ERRORS[_BOOT_OK] = "Successful boot"
_ERRORS[_ERR_CMD_TOO_SHORT] = "Data recieved too short to be a valid command"
_ERRORS[_ERR_CMD_CRC_FAIL] = "The CRC check failed on the command"
_ERRORS[_ERR_CMD_UNKNOWN] = "That command is not known"
_ERRORS[_ERR_CMD_WRONG_LENGTH] = "Not the expected number of bytes recieved"
_ERRORS[_ERR_INVALID_PI_ID] = "The Pi ID sent is invalid"
_ERRORS[_ERR_CMD_NOT_IMPLEMENTED] = "The command is known, but not yet implemented"
_ERRORS[_ERR_COMMS_NOT_READABLE] = "Serial port is not readable"
_ERRORS[_ERR_COMMS_TOO_LONG] = "Too many bytes recieved"
_ERRORS[_ERR_COMMS_BUFFER_LENGTH_MISMATCH] = (
    "The buffer recieved is shorter than the number of bytes it contains!")
_ERRORS[_ERR_COMMS_BUFFER_NOT_LONG_ENGOUGH] = "Cannot fit the response into the buffer"
_ERRORS[_ERR_BUFFER_TOO_SMALL_FOR_ERRORS] = "Too many errors for the length of the comms buffer"
_ERRORS[_ERR_CONFIG_CRC_FAILURE] = "CRC failure when reading the config from EEPROM"
_ERRORS[_ERR_ERRORS_CRC_FAILURE] = "CRC failure when reading the error details from EEPROM"
_ERRORS[_ERR_IAP_ERASE_PREPARE_FAIL] = "Failed to prepare EEPROM for wiping"
_ERRORS[_ERR_IAP_ERASE_FAIL] = "Failed to wipe the EEPROM"
_ERRORS[_ERR_IAP_WRITE_PREPARE_FAIL] = "Failed to prepare the EEPROM for writing"
_ERRORS[_ERR_IAP_WRITE_FAIL] = "Failed to write to EEPROM"
_ERRORS[_ERR_IAP_COMPARE_FAIL] = "Read back from EEPROM failed"
_ERRORS[_ERR_IAP_BLANK_CHECK_FAIL] = "Failed to perform blank check"

def lookup_error(error):
    """
        convert an error code to its string description
    """
    try:
        return _ERRORS[error]
    except KeyError:
        raise InvalidErrorCode("Unknown error code (0x%02X)" % error)

def convert_error_buffer(errors):
    """
        convert and entire error buffer to the string descriptions
    """
    output = []
    for err in errors:
        output.append(lookup_error(err))
    return output
