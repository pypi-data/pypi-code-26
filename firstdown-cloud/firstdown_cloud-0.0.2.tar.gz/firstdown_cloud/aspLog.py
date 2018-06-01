
from email.utils import parsedate_tz
import json
from Crypto.Cipher import AES

class ASPLog:


    """
    Initialize with an empty log lines array.
    """
    def __init__(self):
        self.lines = []

    """
    Return a JSON object from the ASP auto_processed.log file data.
    """
    def parselog(self, filename):
        self.lines = []
        with open(filename, "r") as logfile:
            for line in logfile:
                status = SequenceStatus()
                fields = line.split()
                if len(fields) < 10:
                    continue
                status.duration = fields[5]
                status.name = fields[6]
                status.scid = fields[7]
                status.seqid = fields[8]
                if status.duration: # if string is not empty
                    dateTimeString = "{0} {1} {2} {3} Z".format(fields[2], fields[1], fields[4], fields[3])
                    status.timestamp = parsedate_tz(dateTimeString)
                for word in fields[9:]:
                    status.statusMessage += word + " "
                status.statusMessage = status.statusMessage.rstrip()
                self.lines.append(line)
        return self.lines

    """
    Return an AES encrpyted string of text using the provided key
    """
    def encrypt(self, key):
        linesJson = json.dumps(self.lines)
        lengthDivisibleBy16 = (len(linesJson)/16 + 1) * 16
        linesJson = linesJson.ljust(lengthDivisibleBy16)

        cipher = AES.new(key, AES.MODE_ECB)
        return cipher.encrypt(linesJson)


    """
    Return an AES decrpyted string of text using the provided key
    """
    def decrypt(self, encryptedText, key):
        cipher = AES.new(key, AES.MODE_ECB)
        linesJson = cipher.decrypt(encryptedText)
        return json.loads(linesJson)

class SequenceStatus:

    def __init__(self):
        self.duration = 0
        self.name = ""
        self.scid = ""
        self.seqid = ""
        self.timestamp = ""
        self.statusMessage = ""

    def __str__(self):
        """Return a readable string description of an instance of Overflight"""
        return "Status name: {0} scid: {1} seqid: {2} duration: {3} timestamp: {4}".format(self.name, self.scid,
                                                                                           self.seqid,
                                                                                           str(self.duration),
                                                                                           self.timestamp)


