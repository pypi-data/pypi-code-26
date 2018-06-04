import argparse

import serial

from command.check import Check
from command.delete import Delete
from command.read import Read
from command.send import Send
from command.util.serial_stream import SerialStream


def main():
    parser = argparse.ArgumentParser(prog='sms-cli',
                                     description="execute AT commands on GSM shield module via serial port")
    parser.add_argument("-v", "--version", help="print version number", action='version', version='%(prog)s 1.0.0')
    parser.add_argument("-b", "--baud", help="specify baud rate", required=False, default=19200)
    parser.add_argument("-p", "--port", help="specify port device type", required=False, default="/dev/ttyAMA0")
    sub_parser = parser.add_subparsers()

    send_parser = sub_parser.add_parser('send', help='send SMS message to destination')
    send_parser.add_argument("-d", "--destination",
                             help="destination MSISDN in full format (e.g. +38591234567)", required=True)
    send_parser.add_argument("-m", "--message",
                             help="SMS message text with maximum of 160 characters (e.g. \"Some message text.\")",
                             required=True)

    check_parser = sub_parser.add_parser('read',
                                         help="read all inbound SMS messages from inbox, or just one using index")
    check_parser.add_argument("-i", "--index",
                              help="read only message at this index from the top of inbox", required=False, default=0)
    check_parser.add_argument("-s", "--storage",
                              help="specify the storage from which to read messages, options: [SM | ME | MT | BM | SR]",
                              required=False, default="SM")
    check_parser.add_argument("-u", "--unread", help="read only currently unread messages (when not using index)",
                              required=False, action="store_true")
    check_parser.add_argument("-d", "--dry", help="dry read, not changing status of unread messages while reading",
                              required=False, action="store_true")
    check_parser.add_argument("-f", "--full", help="show full header information of red SMS messages",
                              required=False, action="store_true")

    check_parser = sub_parser.add_parser('delete', help="delete specific message from storage")
    check_parser.add_argument("-i", "--index", help="index of SMS message to delete", required=True)
    check_parser.add_argument("-s", "--storage",
                              help="specify the storage from which to delete message, "
                                   "options: [SM | ME | MT | BM | SR]",
                              required=False, default="SM")

    check_parser = sub_parser.add_parser('check', help="check connectivity with GSM shield module")
    check_parser.add_argument("-n", "--number",
                              help="number of iterations to check connection", required=False, default=4)
    args = parser.parse_args()

    serial_stream = None

    try:
        serial_stream = SerialStream(args.port, args.baud)
        command = create_command(args)
        command.execute(serial_stream)
    except serial.SerialException as e:
        print("Unable to open serial port: " + str(args.port))
        print(e)
    finally:
        if serial_stream is not None:
            serial_stream.close_stream()


def create_command(args):
    if hasattr(args, "destination") and hasattr(args, "message"):
        return Send(args.destination, args.message)
    if hasattr(args, "index") and hasattr(args, "storage") and hasattr(args, "unread") and hasattr(args, "dry") \
            and hasattr(args, "full"):
        return Read(args.index, args.storage, args.unread, args.dry, args.full)
    if hasattr(args, "index") and hasattr(args, "storage"):
        return Delete(args.index, args.storage)
    else:
        return Check(args.number)


if __name__ == "__main__":
    main()
