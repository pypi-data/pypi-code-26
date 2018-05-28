import spidev
import time

CMD_NO_COMMAND                 = 0x00
CMD_GET_PROTOCOL_VERSION       = 0x01
CMD_SET_SENSOR_COUNT           = 0x02
CMD_GET_SENSOR_COUNT           = 0x03
CMD_GET_SENSOR_READING         = 0x04
CMD_SET_INTERVAL               = 0x05
CMD_TOGGLE_LED                 = 0x06
CMD_SET_MAX_DISTANCE           = 0x07
CMD_GET_MAX_DISTANCE           = 0x08
CMD_GET_FIRMWARE_VERSION_MAJOR = 0x09
CMD_GET_FIRMWARE_VERSION_MINOR = 0x0a

class Octasonic:

  def __init__(self, channel):
    self.spi = spidev.SpiDev()
    self.spi.open(0, channel)
    self.spi.mode = 0b00
    self.spi.max_speed_hz = 600 # need to see what speed is really supported
    
    # init and ignore response
    self.send(0x00, 0x00)

  # each send is a half duplex operation with one transfer to send
  # the command then another transfer to receive the results
  def send(self, cmd, param):
    # send the request
    response1 = self.spi.xfer([(cmd<<4)|param])
    # get the response
    response2 = self.spi.xfer([CMD_NO_COMMAND])
    #print "Responses: %s, %s" % (response1, response2)
    return response2[0]

  def get_protocol_version(self):
    return self.send(CMD_GET_PROTOCOL_VERSION, 0x00)

  # note this is new functionality in protocol version 2
  def get_firmware_version(self):
    firmware_major = self.send(CMD_GET_FIRMWARE_VERSION_MAJOR, 0x00)
    firmware_minor = self.send(CMD_GET_FIRMWARE_VERSION_MINOR, 0x00)
    return "%s.%s" % (firmware_major, firmware_minor)

  def set_sensor_count(self, count):
    self.send(CMD_SET_SENSOR_COUNT, count)

  def get_sensor_count(self):
    self.send(CMD_GET_SENSOR_COUNT, 0x00)

  def get_sensor_reading(self, index):
    return self.send(CMD_GET_SENSOR_READING, index)

  def toggle_led(self):
    self.send(CMD_TOGGLE_LED, 0x00)

def main():
  octasonic = Octasonic(0)
  protocol_version = octasonic.get_protocol_version()
  firmware_version = octasonic.get_firmware_version()
  print "Protocol v%s; Firmware v%s" % (protocol_version, firmware_version)
  octasonic.set_sensor_count(8)
  print "Sensor count: %s" % octasonic.get_sensor_count()
  for x in range(0, 100):
    octasonic.toggle_led()
    time.sleep(0.25)
    for i in range(0, 7):
      print octasonic.get_sensor_reading(i),
    print

if __name__ == "__main__":
  main()

