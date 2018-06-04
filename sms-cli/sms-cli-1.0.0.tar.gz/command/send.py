from time import sleep


class Send:
    def __init__(self, destination, message):
        self.destination = str(destination).strip()
        self.message = str(message)
        if not self.destination.startswith("+"):
            self.destination = "+" + self.destination

    def execute(self, serial_stream):
        print("Sending message...")
        serial_stream.write("AT + CMGF = 1\r")
        serial_stream.write("AT + CMGS = \"" + self.destination + "\"\r")
        serial_stream.write(self.message + "\r")
        serial_stream.write(chr(26))
        serial_stream.write("\r")
        sleep(3)
        print("Message sent")
