"""
    Conversions used for the pi stack to get actual values rather than ADC counts
    Philip Basford
    October 2017
"""

_VREF = 3.3  #The reference voltage used in the chip
_ADC_MAX = 65535 #The maximum ADC value possible

#Potential divider details for main voltage in
_VIN_R1 = 100000
_VIN_R2 = 12000

#Details for main current measurement
_CIN_SENSE = 0.039
_CIN_GAIN = 20

#potentional divider details for 5V powersupply
_V5_R1 = 3300
_V5_R2 = 3900

#potential divider details for pi PSU
_PI_R1 = 2000
_PI_R2 = 3000

#details for pi current monitoring circuit
_PI_C_SENSE = 0.05
_PI_C_R_OUT = 3300

#scale factor for ZXCT1009
_ZXCT1009_SF = 100

def convert_vin(reading):
    """
        Convert ADC reading to main input voltage
    """
    return _convert_adc(reading, _VIN_R1, _VIN_R2)

def convert_cin(reading):
    """
        Convert ADC reading to main current reading
    """
    return round(_adc_to_v(reading) / _CIN_GAIN / _CIN_SENSE, 2)

def convert_5v(reading):
    """
        Convert ADC reading to 5v measurement
    """
    return _convert_adc(reading, _V5_R1, _V5_R2)

def convert_pi_v(reading):
    """
        Convert ADC reading to Pi output measurement
    """
    return _convert_adc(reading, _PI_R1, _PI_R2)

def convert_pi_c(reading):
    """
        Convert the pi output current ADC reading to value
    """
    return round((_ZXCT1009_SF * _adc_to_v(reading))/(_PI_C_SENSE * _PI_C_R_OUT), 2)

def convert_power(reading):
    """
        Convert the power reading from the main vin side
    """
    return round(
        reading * pow(_VREF, 2) / pow(_ADC_MAX, 2) *
        (_VIN_R1 + _VIN_R2) / _VIN_R2 / _CIN_SENSE / _CIN_GAIN, 2)

def convert_5v_power(reading):
    """
        Convert the power reading from the 5v/pi side
    """
    return round(
        reading * pow(_VREF, 2) / pow(_ADC_MAX, 2) *
        (_V5_R2 + _V5_R1) / _V5_R2 * _ZXCT1009_SF / (_PI_C_SENSE * _PI_C_R_OUT), 2)

def _convert_adc(adc, res1, res2):
    """
        R1 = the upper of the pair
        R2 = the lower of the pair
    """
    return round(_adc_to_v(adc) * (res1 + res2) / res2, 2)

def _adc_to_v(adc):
    """
        Convert an ADC reading the voltage being put into it
    """
    return adc * _VREF / _ADC_MAX
