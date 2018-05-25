import navio2 as navio
import navio2.ublox
import logging
import coloredlogs
import subprocess
import os.path
from emlid.util.util import root_should_execute
coloredlogs.install()

class GPSTest():
    def __init__(self, **kwargs):
        self.ubl = navio.ublox.UBlox(**kwargs)
        self.ubl.configure_poll_port()
        self.ubl.configure_port(port=navio.ublox.PORT_SERIAL1, inMask=1, outMask=0)
        self.ubl.configure_message_rate(navio.ublox.CLASS_NAV, navio.ublox.MSG_NAV_POSLLH, 1)

    def run(self):
        self.ubl.receive_message_nonblocking()
        return True

class Mpu9250Test():
    def __init__(self, **kwargs):
        try:
            self.sensor = navio.mpu9250.MPU9250(**kwargs)
        except Exception as e:
            raise Exception("Failed to create MPU9250")

    def run(self):
        try:
            if not self.sensor.testConnection():
                raise RuntimeError("No connection!")
            else:
                return True
        except OSError as e:
            raise Exception("Bus error on MPU9250")

class Ms5611Test():
    def __init__(self, **kwargs):
        try:
            self.sensor = navio.ms5611.MS5611(**kwargs)
        except Exception as e:
            raise Exception("Failed to create MS5611")

    def run(self):
        try:
            self.sensor.initialize()
            self.sensor.update()
            pressure = self.sensor.returnPressure()
            t = self.sensor.returnTemperature()
            if (900 < pressure < 1300) and (-40 < t < 80):
                return True
            else:
                raise RuntimeError("Is barometer covered with a foam?")
        except IOError as e:
            raise RuntimeError("No connection!")

class AdcTest():
    def __init__(self, **kwargs):
        try:
            self.sensor = navio.adc.ADC(**kwargs)
        except OSError as e:
            raise

    def run(self):
        try:
            board_voltage = self.sensor.read(0)

            if not 4500 < board_voltage < 5300:
                logging.warning("Please check board voltage ({}V)!".format(board_voltage / 1000.0))

            return 4300 < board_voltage < 5700

        except OSError as e:
            raise Exception("Read error on ADC")

class PwmTest():
    def __init__(self, **kwargs):
        self.pwmchip_path = "/sys/class/pwm/pwmchip0"

    def run(self):
        if not os.path.exists(self.pwmchip_path):
            raise RuntimeError("rcio_pwm module wasn't loaded")

        return True

class RCIOStatusAliveTest():
    def __init__(self, **kwargs):
        self.status_alive_path = "/sys/kernel/rcio/status/alive"

    def run(self):
        if os.path.exists(self.status_alive_path):
            with open(self.status_alive_path) as alive:
                is_alive = alive.read().strip() == "1"
                if not is_alive:
                    raise RuntimeError("RCIO not connected")
        else:
            raise RuntimeError("rcio_status wasn't loaded")

        return True

class LSM9DS1Test():
    def __init__(self, **kwargs):
        try:
            self.sensor = navio.lsm9ds1.LSM9DS1(**kwargs)
        except Exception as e:
            raise Exception("Failed to create LSM9DS1")

    def run(self):
        try:
            if not self.sensor.testConnection():
                raise RuntimeError("No connection!")
            else:
                return True
        except OSError as e:
            raise Exception("Bus error on LSM9DS1")

class ICM20602Test():
    class ICM20602(navio.mpu9250.MPU9250):
        _ICM20602_RESPONSE = 0x12

        def testConnection(self):
            response = self.ReadReg(self._MPU9250__MPUREG_WHOAMI)
            return response == self._ICM20602_RESPONSE

    def __init__(self, **kwargs):
        try:
            self.sensor = self.ICM20602(**kwargs)
        except Exception as e:
            raise Exception("Failed to create ICM20602")

    def run(self):
        try:
            if not self.sensor.testConnection():
                raise RuntimeError("No connection!")
            else:
                return True
        except OSError as e:
            raise Exception("Bus error on ICM20602")

class CanBusTest():
    def __init__(self, **kwargs):
        self.status_path = "/proc/net/can/stats"

    def run(self):
        if os.path.exists(self.status_path):
            with open(self.status_path) as status:
                is_alive = status.read().splitlines()[11].split()[0] != "0"
                if not is_alive:
                    raise RuntimeError("CAN device not connected")
        else:
            raise RuntimeError("CAN status wasn't loaded")
        return True

class ToshibaTest():
    def __init__(self, **kwargs):
        self.command = "vcgencmd get_camera | grep -q 'detected=1'"

    def run(self):
        try:
            subprocess.call(self.command, shell=True)
        except subprocess.CalledProcessError:
            raise RuntimeError("Cannot get information")
        return True

