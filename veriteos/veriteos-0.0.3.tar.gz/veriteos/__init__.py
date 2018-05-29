import requests
import time
import base64
import hashlib

from sawtooth_signing import create_context
from sawtooth_signing import CryptoFactory, ParseError
from sawtooth_signing.secp256k1 import Secp256k1PrivateKey

from sawtooth_sdk.protobuf.transaction_pb2 import Transaction, TransactionHeader
from sawtooth_sdk.protobuf.batch_pb2 import BatchList, BatchHeader, Batch

from .veriteos_exceptions import VeriteosException


VERITEOS_ENDPOINT = 'https://api.veriteos.com/v1'


class Client(object):

	def __init__(self, api_key, transaction_family, transaction_family_version):
		self.api_key = api_key
		self.transaction_family = transaction_family
		self.transaction_family_version = transaction_family_version
		"""
		try:
			with open(keyfile) as f:
				private_key_str = f.read().strip()
		except OSError as e:
			raise VeriteosException(
        		'Failed to read private key {}: {}'.format(keyfile, str(e)))

		try:
			private_key = Secp256k1PrivateKey.from_hex(private_key_str)
		except ParseError as e:
			raise VeriteosException(
				'Unable to load private key: {}'.format(str(e)))

		self._signer = CryptoFactory(create_context('secp256k1')) \
			.new_signer(private_key)
		"""

	def _sha512(self, data):
		self.data = data
		return hashlib.sha512(data).hexdigest()


	def _serialize_data(self, data):
		"""
		Serialization is just a delimited utf-8 encoded string.
		"""
		self.data = data
		payload = ",".join([name, action, str(space)]).encode()
		return payload


	def _encode_address(self, transaction_family, address):
		self.transaction_family = transaction_family
		self.address = address
		transaction_family = self._sha512(transaction_family.encode('utf-8'))[0:6]
		address = self._sha512(address.encode('utf-8'))[0:64]
		return transaction_family + address


	def _create_batch_list(self, transactions):
		self.transactions = transactions
		transaction_signatures = [t.header_signature for t in transactions]

		header = BatchHeader(
			signer_public_key=self._signer.get_public_key().as_hex(),
			transaction_ids=transaction_signatures
		).SerializeToString

		signature = self._signer.sign(header)

		batch = Batch(
			header=header,
			transactions=transactions,
			header_signature=signature
		)

		return BatchList(batches=[batch])


	def send(self, address, data):
		"""
		Send batched transaction for `address` to /state endpoint.
		"""
		self.address = address
		self.data = data
		address = _encode_address(self.transaction_family, address)
		
		payload = _serialize_data(data)
		signature = self._signer.get_public_key().as_hex()

		header = TransactionHeader(
			signer_public_key=self._signer.get_public_key().as_hex(),
			family_name=transaction_family,
			family_version=transaction_family_version,
			input=[address],
			output=[address],
			dependencies=[],
			payload=sha512(payload),
			batcher_public_key=signature,
			nonce=time.time().hex().encode
		).SerializeToString()

		transaction = Transaction(
			header=header,
			payload=payload,
			header_signature=signature
		)
		
		batch_list = self._create_batch_list([transaction])

		url = VERITEOS_ENDPOINT + '/batches'
		r = requests.post(url, auth=(self.api_key, ''), data=payload)
		response = r.json()
		data = base64.b64decode(response["data"]).decode()
		return data


	def read_address(self, address=None):
		"""
		Read state of given address from /state endpoint.
		"""
		self.address = address
		address = self._encode_address(self.transaction_family, address)
		url = VERITEOS_ENDPOINT + '/state/{}'.format(address)
		r = requests.get(url, auth=(self.api_key, ''), verify=False)
		response = r.json()
		data = base64.b64decode(response["data"]).decode()
		return data
