"""Unofficial Cleware USB-ADC 2 Python module.

This module allows the readout of the Cleware USB-ADC2 analog-digital-converter
(http://www.cleware-shop.de/USB-ADC2) using the hidapi library.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""

from __future__ import with_statement
from __future__ import print_function
import hid, time

class ClewareADC(object):
    """Class to access the Cleware USB-ADC2.
    
    The communication with the Cleware USB-ADC2 can either be established
    by using the openDevice() and closeDevice() methods or by using the
    *with* statement.

    Attributes:
        serialNumber (int): The serial number of the USB-ADC2 to use.
        maxV (float): Scaling factor to apply to the output.
    """

    vendorId = 0x0d50
    productId = 0x0050

    def __init__(self, maxV, serialNumber=None):
        """ClewareADC constructor.

        Initialises a ClewareADC instance, but does not yet open a connection
        to the ADC.

        Args:
            maxV (float): Scaling factor to apply to the output. The USB-ADC2 comes
                          in 5.181V, 13.621V and 24.704V variants.
            serialNumber (Optional[int]): Serial number of the ADC to use. Can either
                                          supplied in the constructor or via
                                          openDevice().
        """
        self._requestCount = 0
        self.serialNumber = serialNumber
        self.maxV = maxV
        self._maxReadRetries = 50
        self._maxSendRetries = 3
        self._waitBetweenSends = 0.1

    def __enter__(self):
        self.openDevice()
        return self

    def __exit__(self, eType, eValue, eTraceback):
        self.closeDevice()
        
    @staticmethod
    def listDevices():
        """Static method to list all connected USB-ADC2 devices.
        
        This static method can be used to enumerate all USB-ADC2 devices.

        Note:
            For some reason the serial number can not be read via hidapi under OSX.

        Returns:
            list: A list containing 2-tuple. The first element in the tuple contains 
            the USB path of the device, the second element contains the serial number.
        """
        result = []

        hidEnum = hid.enumerate()
        for dev in hidEnum:
            if dev['vendor_id'] == ClewareADC.vendorId and dev['product_id'] == ClewareADC.productId:
                result.append((dev['path'].decode('ascii'), int(dev['serial_number'], 16)))

        return result

    def openDevice(self, serialNumber=None):
        """Open a USB-ADC2 device.

        If serialNumber is not None, the device with the given serial number is opened,
        otherwise the serial number supplied to the constructor is used.

        Args:
            serialNumber (Optional[int]): Serial number of the ADC to open. If None is given,
                                          the serial number supplied to the constructor is used.

        Raises:
            IOError: If the USB-ADC2 with the requested serial number could not be found.
        """
        if serialNumber is not None:
            self.serialNumber = serialNumber

        hidEnum = hid.enumerate()
        self.path = None
        for dev in hidEnum:
            if dev['vendor_id'] == self.vendorId and dev['product_id'] == self.productId:
                if int(dev['serial_number'], 16) == self.serialNumber:
                    self.path = dev['path']

        if self.path is None:
            raise IOError('Could not find ADC with serial number {}'.format(self.serialNumber))

        self.handle = hid.device()
        self.handle.open_path(self.path)
        self.resetDevice()
    
    def closeDevice(self):
        """Close the connection to the USB-ADC2 device.
        
        Closes the open hidapi handle to the USB-ADC2 device.
        """
        self.handle.close()

    def resetDevice(self):
        """Send a reset command to the USB-ADC2.

        The device is automatically reset when it is opened, but can be reset again
        using this command in case it gets stuck.
        """
        self.handle.write([0x00, 0x03, 0x00, 0x00])
        self.handle.write([0x00, 0x02, 0x03, 0x00])
        self.handle.write([0x00, 0x06, 0x02, 0x00])

    def readChannel(self, channel):
        """Read data from one of the USB-ADC2 channels.

        Tries to read data from one of the two USB-ADC2 channels. 

        Args:
            channel (int): Either 0 for channel 0 or 1 for channel 1.
            
        Returns:
            float: Voltage read on the selected channel.

        Raises:
            ValueError: If channel is neither 0 nor 1.
            IOError: If the USB-ADC2 did not answer after several retries.
        """
        if (channel != 0) and (channel != 1):
            raise ValueError('Invalid channel')

        self._sendReadRequest(channel)

        answerCount = 0
        resendCount = 0
        while True:
            result = self.handle.read(4)
            if (result[1] == self._requestCount) and ((result[0]&0x0F) == channel):
                return ((result[2]*255+result[3])/4096.0)*self.maxV
            
            answerCount += 1
            if answerCount > self._maxReadRetries:
                answerCount = 0
                resendCount += 1
                if resendCount > self._maxSendRetries:
                    raise IOError('ADC did not answer in time')
                self._sendReadRequest(channel)
                time.sleep(self._waitBetweenSends)

    def _sendReadRequest(self, channel):
        self._requestCount += 1
        if (self._requestCount > 0xFF):
            self._requestCount = 0

        self.handle.write([0x00, 0x05, channel, self._requestCount])

def main():
    deviceList = ClewareADC.listDevices()
    if len(deviceList) < 1:
        print('No ADCs found')
        return

    for device in deviceList:
        print('Found ADC at {} with serial number {}'.format(device[0], device[1]))
    print('')

    with ClewareADC(13.621, deviceList[0][1]) as adc:
        print('Reading from ADC {} with 13.621V scaling:'.format(deviceList[0][1]))

        for i in range(10):
            ch0 = adc.readChannel(0)
            ch1 = adc.readChannel(1)
            print('  Ch 0: {}V, Ch 1: {}V'.format(ch0, ch1))
            time.sleep(1.00)

if __name__ == '__main__':
    main()

