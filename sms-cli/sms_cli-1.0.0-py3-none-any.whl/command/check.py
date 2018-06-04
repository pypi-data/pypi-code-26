from time import sleep


class Check:
    def __init__(self, number):
        self.number = int(number)

    def execute(self, serial_stream):
        print("Checking connection...")
        ok_count = 0
        for i in range(self.number):
            serial_stream.write("AT\r")
            sleep(2)
            response = serial_stream.readline()
            if response.startswith("OK"):
                ok_count += 1
            print(str(i + 1) + "/" + str(self.number) + " AT -> " + response)
        if ok_count == self.number:
            print("Connection stable")
        else:
            print("Connection unstable, sent " + str(self.number) + " requests but received " +
                  str(ok_count) + " OK responses")
