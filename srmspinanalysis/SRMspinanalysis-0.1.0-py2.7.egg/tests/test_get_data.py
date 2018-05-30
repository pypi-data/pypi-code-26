import numpy as np
from .. import get_data

def test_extract_RASP_data_1():
    # Standard url of RASP data from thrustcurve.org.
    url1 = 'http://www.thrustcurve.org/simfilesearch.jsp?id=1247'
    # From thrustcurve.org
    url1_time = np.array([0.016, 0.044, 0.08, 0.088, 0.096, 0.105, 0.116,
                          0.129, 0.131, 0.135, 0.139, 0.143, 0.149, 0.157, 
                          0.173, 0.187, 0.194, 0.197, 0.202, 0.206, 0.213,
                          0.218, 0.227, 0.236, 0.241, 0.25])
    # From function
    SRM1 = get_data.SolidRocketMotor(url1)
    assert np.array_equal(url1_time, SRM1.motor_time_data[1:])
    
def test_extract_RASP_data_2():
    # Standard url of RASP data from thrustcurve.org.
    url2 = 'http://www.thrustcurve.org/simfilesearch.jsp?id=641'
    # From thrustcurve.org
    url2_thrust = np.array([16.299, 21.959, 30.785, 35.774, 37.577, 38.220,
                            37.357, 37.577, 35.093, 32.378, 27.168, 26.938,
                            25.125, 21.729, 16.980, 12.682, 7.471, 3.169,
                            1.584, 0.679, 0.000])
    # From function
    SRM2 = get_data.SolidRocketMotor(url2)
    assert np.array_equal(url2_thrust, SRM2.motor_thrust_data[1:])

def test_extract_RASP_data_3():
    # Tests several url's to make sure no parsing errors occur.
    url_list = ['http://www.thrustcurve.org/simfilesearch.jsp?id=1252',
                'http://www.thrustcurve.org/simfilesearch.jsp?id=2003',
                'http://www.thrustcurve.org/simfilesearch.jsp?id=641']
    for url in url_list:
        get_data.extract_RASP_data(url)