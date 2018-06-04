import serial
from time import sleep


class SerialStream:
    def __init__(self, com, baud, timeout=1, encoding="ascii", pause_sec=0.1):
        self.ser = serial.Serial(com, baud, timeout=timeout)
        self.encoding = encoding
        self.pause_sec = pause_sec
        self.open_stream_if_closed()

    def write(self, data):
        self.open_stream_if_closed()
        self.ser.write(data.encode(self.encoding))
        sleep(self.pause_sec)
        _ = self.ser.readline()  # Read and ignore echoed bytes

    def readline(self):
        self.open_stream_if_closed()
        return self.ser.readline().decode(self.encoding)

    def readlines(self):
        self.open_stream_if_closed()
        lines = []
        for line in self.ser.readlines():
            lines.append(line.decode(self.encoding))
        return lines

    def open_stream_if_closed(self):
        if not self.ser.isOpen():
            self.ser.open()

    def close_stream(self):
        self.ser.close()
