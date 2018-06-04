# -*- coding: utf-8 -*-
# @Time    : 2018/6/3 下午9:27
# @Author  : GuoXiaoMin
# @File    : Transaction.py
# @Software: PyCharm
import enum
import time
from sdk.src.proto.generated.corepb import transaction_pb2
from sdk.src.core.Address import Address
from sdk.src.crypto.hash.Hash import Hash
from sdk.src.crypto.keystore.secp256k1.ECsignature import ECsignature
from sdk.src.crypto.keystore.Algorithm import Algorithm
import base64


class Transaction:

    # TransactionMaxGasPrice max gasPrice:1 * 10 ** 12
    __TransactionMaxGasPrice = 1000000000000

    # TransactionMaxGas max gas:50 * 10 ** 9
    __TransactionMaxGas = 50000000000

    # TransactionGasPrice default gasPrice : 10**6
    __TransactionGasPrice = 1000000

    # MinGasCountPerTransaction default gas for normal transaction
    __MinGasCountPerTransaction = 20000

    # GasCountPerByte per byte of data attached to a transaction gas cost
    __GasCountPerByte = 1

    # MaxDataPayLoadLength Max data length in transaction
    __MaxDataPayLoadLength = 1024 * 1024

    # MaxDataBinPayloadLength Max data length in binary transaction
    __MaxDataBinPayloadLength = 64

    class PayloadType(enum.Enum):

        BINARY = "binary"
        DEPLOY = "deploy"
        CALL = "call"

        def __init__(self, _type):
            self.__type = _type

        @property
        def get_type(self):
            return self.__type

    def __init__(self, chain_id, from_account, to_addr, value, nonce, payload_type, payload, gas_price, gas_limit):

        if gas_price > self.__TransactionMaxGasPrice or gas_price > self.__TransactionMaxGas:
            raise Exception("invalid gasPrice")

        if payload is not None and len(payload) > self.__MaxDataPayLoadLength:
            raise Exception("payload data length is out of max length")


        self.__chain_id = chain_id
        self.__from_account = from_account
        self.__from_addr = from_account.get_address_obj()

        self.__to_addr = to_addr
        self.__value = value
        self.__nonce = nonce
        self.__gas_price = gas_price
        self.__gas_limit = gas_limit
        self.__timestamp = int(round(time.time() * 1000))

        transaction = transaction_pb2.Transaction()
        setattr(transaction.data, 'payload', payload)
        setattr(transaction.data, 'payload_type', payload_type.get_type)
        self.__data = transaction.data


    def get_hash(self):
        return self.__hash

    def set_hash(self, hash):
        self.__hash = hash

    def get_from(self):
        return self.__from_addr

    def set_from(self, from_addr):
        self.__from_addr = from_addr

    def get_to(self):
        return self.__to_addr

    def set_to(self, to_addr):
        self.__to_addr = to_addr

    def get_value(self):
        return self.__value

    def set_value(self, value):
        self.__value = value

    def get_nonce(self):
        return self.__nonce

    def set_nonce(self,nonce):
        self.__nonce = nonce

    def get_timestamp(self):
        return self.__timestamp

    def set_timestamp(self, timestamp):
        self.__timestamp = timestamp

    def get_chain_id(self):
        return self.__chain_id

    def set_chain_id(self, chain_id):
        self.__chain_id = chain_id

    def get_gas_price(self):
        return self.__gas_price

    def set_gas_price(self, gas_price):
        self.__gas_price = gas_price

    def get_gas_limit(self):
        return self.__gas_limit

    def set_gas_limit(self, gas_limit):
        self.__gas_limit = gas_limit

    def get_alg(self):
        return self.__alg

    def set_alg(self, alg):
        self.__alg = alg

    def get_sign(self):
        return self.__sign

    def set_sign(self, sign):
        self.__sign = sign

    def get_data(self):
        return self.__data

    def set_data(self, data):
        self.__data = data

    def from_proto(self, msg: bytes):
        transaction = transaction_pb2.Transaction()
        transaction.ParseFromString(msg)
        self.orgtx=transaction;
        print(transaction)
        self.set_hash(bytearray(transaction.hash))
        self.set_from(Address.parse_from_bytes(bytearray(getattr(transaction, "from"))))
        self.set_chain_id(transaction.chain_id)
        self.set_gas_price(self.bytes2integer(bytearray(transaction.gas_price)))
        self.set_gas_limit(self.bytes2integer(bytearray(transaction.gas_limit)))
        self.set_nonce(transaction.nonce)
        self.set_alg(Algorithm(transaction.alg))
        self.set_sign(transaction.sign)
        self.set_timestamp(transaction.timestamp)
        self.set_to(Address.parse_from_bytes(bytearray(getattr(transaction, "to"))))
        self.set_value(self.bytes2integer(bytearray(transaction.value)))

        if transaction.data is None:
            raise Exception("invalid transaction data")

        if len(bytearray(transaction.data.payload)) > self.__MaxDataPayLoadLength:
            raise Exception("payload data length is out of max length")

        self.set_data(transaction.data)
        ##print(self.__dict__)


    def to_proto(self) -> str:
        print("=================")
        transaction = transaction_pb2.Transaction()
        setattr(transaction, 'alg', self.__alg.get_type)
        setattr(transaction, 'chain_id', self.__chain_id)
        setattr(transaction, 'from', bytes(self.__from_addr.bytes()))
        setattr(transaction, 'to', bytes(self.__to_addr.bytes()))
        setattr(transaction, 'value', self.integer2bytes(self.__value))
        setattr(transaction, 'gas_limit', self.integer2bytes(self.__gas_limit))
        setattr(transaction, 'gas_price', self.integer2bytes(self.__gas_price))
        setattr(transaction, 'nonce', self.__nonce)
        setattr(transaction, 'hash', bytes(self.__hash))
        setattr(transaction, 'sign', self.__sign)
        setattr(transaction, 'timestamp', self.__timestamp)
        setattr(transaction.data, 'payload', self.__data.payload)
        setattr(transaction.data, 'payload_type', self.__data.payload_type)

        '''
        print(transaction)
        print(transaction.alg == self.orgtx.alg)
        print(transaction.chain_id == self.orgtx.chain_id)
        print(getattr(transaction, "from") == getattr(self.orgtx, "from"))
        print(getattr(transaction, "to") == getattr(self.orgtx, "to"))
        print(transaction.value == self.orgtx.value)
        print(transaction.gas_limit == self.orgtx.gas_limit)
        print(transaction.gas_price == self.orgtx.gas_price)
        print("nonce")
        print(transaction.nonce == self.orgtx.nonce)
        print(transaction.hash == self.orgtx.hash)
        print(transaction.sign == self.orgtx.sign)
        print(transaction.timestamp == self.orgtx.timestamp)
        print(transaction.data == self.orgtx.data)
        '''
        return base64.b64encode(transaction.SerializeToString()).decode("utf-8")

    def calculate_hash(self):
        hash = Hash.sha3256(
                        bytes(self.__from_addr.bytes()),
                        bytes(self.__to_addr.bytes()),
                        self.integer2bytes(self.__value),
                        self.long2bytes(self.__nonce),
                        self.long2bytes(self.__timestamp),
                        self.__data.SerializeToString(),
                        self.int2bytes(self.__chain_id),
                        self.integer2bytes(self.__gas_price),
                        self.integer2bytes(self.__gas_limit)
                         )
        self.__hash = hash
        return self.__hash

    def sign(self):
        signature = ECsignature()
        pri_key = self.__from_account.get_private_key_obj()
        signature.init_sign(pri_key)
        sign = signature.sign(self.__hash)
        self.__alg = Algorithm(signature.algorithm())
        self.__sign = sign.to_bytes()

    @classmethod
    def bytes2integer(cls, arr):
        res = 0
        for i in range(len(arr)):
            res = (res << 8) + arr[i]
        print(res)
        return res

    @classmethod
    def integer2bytes(cls, num):
        res = bytearray(16)
        for i in range(16)[::-1]:
            res[i] = num % 256
            num = (num >> 8)
        return bytes(res)

    @classmethod
    def long2bytes(cls, num):
        res = bytearray(8)
        for i in range(8)[::-1]:
            res[i] = num % 256
            num = (num >> 8)
        return bytes(res)

    @classmethod
    def int2bytes(cls, num):
        res = bytearray(4)
        for i in range(4)[::-1]:
            res[i] = num % 256
            num = (num >> 8)
        return bytes(res)