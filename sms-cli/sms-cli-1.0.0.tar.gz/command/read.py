from time import sleep


class Read:
    def __init__(self, index, storage, unread, dry, full):
        self.index = int(index)
        self.storage = str(storage)
        self.unread = bool(unread)
        self.dry = bool(dry)
        self.full = bool(full)

    def execute(self, serial_stream):
        print("Reading message/s...")
        serial_stream.write("AT + CMGF = 1\r")
        serial_stream.write("AT + CSDH = " + self.show_code() + "\r")
        serial_stream.write("AT + CPMS = \"" + self.storage + "\"\r")
        if self.index != 0:
            serial_stream.write("AT + CMGR = " + str(self.index) + "," + self.mode() + "\r")
        else:
            serial_stream.write("AT + CMGL = \"" + self.read_status() + "\"," + self.mode() + "\r")
        sleep(1)
        response_lines = serial_stream.readlines()
        for line in response_lines:
            print(line)
        print("Message/s read")

    def show_code(self):
        if self.full:
            return "1"
        else:
            return "0"

    def read_status(self):
        if self.unread:
            return "REC UNREAD"
        else:
            return "ALL"

    def mode(self):
        if self.dry:
            return "1"
        else:
            return "0"
