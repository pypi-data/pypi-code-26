# yichin.py
from binascii import hexlify as yichin_hex
from binascii import unhexlify as yichin_unhex

YICHIN_NUMBER = 8288
YICHIN_ENCODE = "utf-8"
YICHIN_STRING = "yichin"

yichin_chr = lambda x: chr(x)
yichin_int = lambda x, y: int(x, y)
yichin_str = lambda x, y: str(x, y)
yichin_join = lambda x: ''.join(x)
yichin_bytes = lambda x, y: bytes(x, y)
yichin_strip = lambda x, y: x.strip(y)

def encode(yichins):
	return yichin_join([YICHIN_STRING[:3]] + [yichin_chr(yichin_int(yichin, 16) + YICHIN_NUMBER) for yichin in yichin_str(yichin_hex(yichin_bytes(yichins, YICHIN_ENCODE)), YICHIN_ENCODE)] + [YICHIN_STRING[3:]])

def decode(yichins):
	return yichin_str(yichin_unhex(yichin_join([hex(ord(yichin) - YICHIN_NUMBER)[2:] for yichin in yichin_strip(yichins, YICHIN_STRING)])), YICHIN_ENCODE)
