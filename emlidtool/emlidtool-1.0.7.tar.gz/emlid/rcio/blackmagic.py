class Blackmagic:
    @staticmethod
    def start():
        print("Listening on TCP:4242")
        print("Resetting TAP")
        print("Change state to Shift-IR")
        print("Scanning out IRs")
        print("jtag_scan: Sanity check failed: IR[0] shifted out as 0")
        print("platform_init executuon. jtag_scan returns -1Entring GDB protocol main loop")

if __name__ == '__main__':
    server = Blackmagic()
    server.start()
