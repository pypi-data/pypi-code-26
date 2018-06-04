from time import sleep


class Delete:
    def __init__(self, index, storage):
        self.index = int(index)
        self.storage = str(storage)

    def execute(self, serial_stream):
        print("Deleting message...")
        serial_stream.write("AT + CMGF = 1\r")
        serial_stream.write("AT + CPMS = \"" + self.storage + "\"\r")
        serial_stream.write("AT + CMGD = " + str(self.index) + "\r")
        sleep(1)
        print("Message deleted")
