#!/usr/bin/env python3
# stak.py - A STRAKS utility library
# Licence: Apache Licence
# Origin Author: Simon Volpert 
# Port Maintainer: STRAKS Developers
# Project page: https://github.com/straks/strakspos

import urllib.request
import json
import random
import sys
import datetime
from collections import namedtuple
#optional import pycoin.key

MAX_ERRORS = 10
exchanges = [
	{
		'url': 'https://api.coinmarketcap.com/v1/ticker/straks/?convert={cur}',
		'price_key': '0.price_{cur_lower}',
	}
]
explorers = [
	{
		'url': 'https://api.straks.info/v2/addr/{address}',
		'tx_url': 'https://api.straks.info/v2/tx/{txid}',
		'balance_key': 'balance',
		'confirmed_key': 'balance',
		'unconfirmed_key': None,
		'last_tx_key': 'transactions.0',
		'tx_time_key': 'time',
		'tx_inputs_key': 'vin',
		'tx_in_double_spend_key': 'doubleSpentTxID',
		'tx_outputs_key': 'vout',
		'tx_out_value_key': 'value',
		'tx_out_address_key': 'scriptPubKey.addresses.0',
		'tx_double_spend_key': None,
		'tx_fee_key': 'fees',
		'tx_size_key': 'size',
		'tx_confirmations_key': 'confirmations',
		'unit_satoshi': False,
		'prefixes': 'S',
	}
]

# Initialize explorer and exchange list
random.seed()
random.shuffle(explorers)
for _server in explorers:
	_server['name'] = '.'.join(_server['url'].split('/')[2].split('.')[-2:])
for _server in exchanges:
	_server['name'] = '.'.join(_server['url'].split('/')[2].split('.')[-2:])


def stak(amount):
	'''Return a native STAK amount representation'''
	result = ('%.8f' % amount).rstrip('0.')
	if result == '':
		return '0'
	return result


def bits(amount):
	'''Return the amount represented in bits/cash'''
	bit, sat = fiat(amount * 1000000).split('.')
	sat = sat.rstrip('0')
	if sat == '':
		return bit
	return(bit + '.' + sat)


def fiat(amount):
	'''Return the amount represented in a dollar/cent notation'''
	return ('%.2f' % amount)


def jsonload(url):
	
	'''Load a web page and return the resulting JSON object'''
	request = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
	try:

		with urllib.request.urlopen(request) as webpage:
			data = str(webpage.read(), 'UTF-8')
			data = json.loads(data)
			return data

	except Exception as e:

		# Fix for STRAKS, API will send back a 422 Unprocessable if an address has not recieved funds yet
		# Send back blank data
		if "Unprocessable" in str(e):
			return {}
		


def get_value(json_object, key_path):
	'''Get the value at the end of a dot-separated key path'''
	# Make sure the explorer did not return an error
	if 'err_no' in json_object:
		if json_object['err_no'] == 1:
			raise urllib.error.HTTPError(None, 404, 'Resource Not Found', None, None)
		elif json_object['err_no'] == 2:
			raise urllib.error.HTTPError(None, 400, 'Parameter Error', None, None)
	for k in key_path.split('.'):
		# Process integer indices
		try:
			k = int(k)
		except ValueError:
			pass
		# Expand the key
		try:
			json_object = json_object[k]
		except (TypeError, IndexError):
			# The key rightfully doesn't exist
			return False
	return json_object


def get_price(currency, exchange=exchanges[0]['name']):
	'''Get the current STRAKS price in the desired currency'''
	found = False
	currency = currency.strip()
	for server in exchanges:
		if server['name'] == exchange:
			found = True
			break
	if not found:
		raise KeyError('{src} is not in list of exchanges'.format(src=exchange))
	data = jsonload(server['url'].format(cur=currency, cur_lower=currency.lower()))
	rate = float(get_value(data, server['price_key'].format(cur=currency, cur_lower=currency.lower())))
	if rate == 0.0:
		raise ValueError('Returned exchange rate is zero')
	return round(rate, 2)


def pick_explorer(server_name=None, address_prefix=None):
	'''Advance the list of explorers until one that matches the requirements is found'''
	for __ in explorers:
		# Cycle to the next server
		server = explorers.pop(0)
		if server is None:
			raise StopIteration('Server list depleted')
		explorers.append(server)
		# Populate server error count if necessary
		if 'errors' not in server:
			server['errors'] = 0
			server['last_error'] = None
			server['last_data'] = None
		# Filter by server name
		if server_name is not None and server['name'] != server_name:
			continue
		# Filter by error rate
		if server['errors'] > MAX_ERRORS and server['name'] != server_name:
			continue
		# Filter by address prefix
		if address_prefix is not None and address_prefix not in server['prefixes']:
			continue
		return server
	raise KeyError('No servers match the requirements')


class AddressInfo(object):
	'''A representation of a block explorer's idea of a STRAKS address state

		Provided properties:
		address         (str) the address in cash format
		confirmed       (float) the confirmed balance of the address
		unconfirmed     (float) the unconfirmed balance of the address
		'''

	def __init__(self, address, explorer=None, verify=False):
		'''Keyword arguments:
		address         (str) straks_address or tuple(str xpub, int index)
		explorer        (str) the name of a specific explorer to query
		verify          (bool) the results should be verified with another explorer
		'''

		# Incompatible parameters
		if verify and explorer is not None:
			raise ValueError('The "verify" and "explorer" parameters are incompatible')
		# Generated address request
		xpub = None
		idx = None
		if type(address) is tuple:
			xpub, idx = address

		self.address = address

		try:
			if xpub is not None:
				self.address = generate_address(xpub, idx)
		except ImportError:
			if xpub is not None:
				raise
		# Add a temporary separator
		explorers.append(None)
		results = []
		# Figure out specific address type availability
		prefixes = 'S'

		blank_template = {'addrStr': self.address, 'balance': 0, 'balanceSat': 0, 'totalReceived': 0, 'totalReceivedSat': 0, 'totalSent': 0, 'totalSentSat': 0, 'txAppearances': 0, 'transactions': []}




		while explorers[0] is not None:
			# Query the next explorer
			if prefixes == 'S':
				server = pick_explorer(explorer)

			else:
				server = pick_explorer(explorer, address_prefix=prefixes[0])
			# Try to get balance
			try:
				# Get and cache the received data for possible future analysis
				json = jsonload(server['url'].format(address=self.address))
				if not json:
					json = blank_template
				server['last_data'] = json
				# Conditional balance processing
				# TODO: This is a mighty convoluted way of doing it and needs rethinking
				if server['confirmed_key'] is not None and server['unconfirmed_key'] is not None:
					confirmed = float(get_value(json, server['confirmed_key']))
					unconfirmed = float(get_value(json, server['unconfirmed_key']))
				elif server['confirmed_key'] is not None and server['balance_key'] is not None:
					confirmed = float(get_value(json, server['confirmed_key']))
					balance = float(get_value(json, server['balance_key']))
					unconfirmed = balance - confirmed
				elif server['unconfirmed_key'] is not None and server['balance_key'] is not None:
					balance = float(get_value(json, server['balance_key']))
					unconfirmed = float(get_value(json, server['unconfirmed_key']))
					confirmed = balance - unconfirmed
				else:
					raise RuntimeError('Cannot figure out address balance')
				# Get the last txid
				try:
					txid = get_value(server['last_data'], server['last_tx_key'])
				except (KeyError, IndexError):
					txid = None
				if not txid:
					txid = None
			except KeyboardInterrupt:
				explorers.remove(None)
				raise
			except:
				server['errors'] += 1
				exception = sys.exc_info()[1]
	
				try:
					server['last_error'] = str(exception.reason)
				except AttributeError:
					server['last_error'] = str(exception)
				if server['errors'] > MAX_ERRORS:
					print('Excessive errors from {server}, disabling. Last error: {error}'.format(server=server['name'], error=server['last_error']))
				continue
			# Convert balances to native units
			if server['unit_satoshi']:
				confirmed /= 100000000
				unconfirmed /= 100000000
			if server['errors'] > 0:
				server['errors'] -= 1
			data = (confirmed, unconfirmed, txid)
			if verify:
				if data not in results:
					results.append(data)
					continue
			results.append(data)

			break
		# If the end of the server list was reached without a single success, assume a network error
		explorers.remove(None)
		if results == []:
			for server in explorers:
				if server['errors'] > 0:
					server['errors'] -= 1
			raise ConnectionError('No results from any known block explorer')
		# Populate instance attributes
		self.confirmed, self.unconfirmed, self.last_txid = results[-1]


def get_balance(address, explorer=None, verify=False):
	'''Get the current balance of an address from a block explorer
	Takes the same arguments as AddressInfo()
	Returns tuple(confirmed_balance, unconfirmed_balance)
	'''
	addr = AddressInfo(address, explorer, verify)
	return addr.confirmed, addr.unconfirmed


def get_last_txid(address, explorer=None, verify=False):
	'''Get the last tx associated with an address
	Takes the same arguments as AddressInfo()
	Returns str(txid)
	'''
	addr = AddressInfo(address, explorer, verify)
	return addr.last_txid


class TxNotFoundError(Exception):
	'''Raised when a requested txid is not known to any block explorer'''


class TxInfo(object):
	'''A representation of a block explorer's idea of a STRAKStransaction

		Provided properties:
		time          (datetime) the time this transaction was first seen or mined
		outputs       (dict) a mapping of receiving addresses to receiving values
					both address formats are provided if possible
		double_spend  (bool) whether or not this transaction has a competing transaction
		fee           (float) the transaction fee
		confirmations (int) the number of confirmations this transaction has

		Will raise TxNotFoundError if the passed txid is not known to any explorer
		'''

	def __init__(self, txid, explorer=None):
		'''Keyword arguments:

		txid         (str) the txid to look for
		explorer     (str) the name of a specific explorer to query
		'''
		# Add a temporary separator
		explorers.append(None)
		#tx_size = 10
		while explorers[0] is not None:
			# Query the next explorer
			try:
				server = pick_explorer(explorer)
			except StopIteration:
				break
			try:
				# Get and cache the received data for possible future analysis

				json = jsonload(server['tx_url'].format(txid=txid))

				server['last_data'] = json
				# Figure out if the tx is a double spend
				if server['tx_double_spend_key'] is not None:
					self.double_spend = get_value(json, server['tx_double_spend_key'])
				else:
					self.double_spend = False
					for i, __ in enumerate(get_value(json, server['tx_inputs_key'])):
						#tx_size += 148
						if get_value(json, '.'.join([server['tx_inputs_key'], str(i), server['tx_in_double_spend_key']])) is not None:
							self.double_spend = True
				# Assemble list of output values
				self.outputs = {}
				for i, __ in enumerate(get_value(json, server['tx_outputs_key'])):
					#tx_size += 34
					addr = get_value(json, '.'.join([server['tx_outputs_key'], str(i), server['tx_out_address_key']]))
					value = float(get_value(json, '.'.join([server['tx_outputs_key'], str(i), server['tx_out_value_key']])))
					if server['unit_satoshi']:
						value /= 100000000
					self.outputs[addr] = value
					# Provide both address formats if possible
					try:
						self.outputs[convert_address(addr)] = value
					except ImportError:
						pass
				# Figure out the tx size and fee
				self.fee = float(get_value(json, server['tx_fee_key']))
				#self.size = tx_size
				self.size = get_value(json, server['tx_size_key'])
				if server['unit_satoshi']:
					self.fee /= 100000000
				self.fee_per_byte = self.fee / self.size * 100000000
				self.time = datetime.datetime.fromtimestamp(get_value(json, server['tx_time_key']))
				self.confirmations = get_value(json, server['tx_confirmations_key'])
				break
			except KeyboardInterrupt:
				explorers.remove(None)
				raise
			except:
				exception = sys.exc_info()[1]
				if isinstance(exception, urllib.error.HTTPError) and exception.code == 404:
					continue
				server['errors'] += 1
				try:
					server['last_error'] = str(exception.reason)
				except AttributeError:
					server['last_error'] = str(exception)
				if server['errors'] > MAX_ERRORS:
					print('Excessive errors from {server}, disabling. Last error: {error}'.format(server=server['name'], error=server['last_error']))
				continue
		try:
			explorers.remove(None)
		except ValueError:
			pass
		if self.__dict__ == {}:
			raise TxNotFoundError('No results from any known block explorer')


def get_tx_propagation(txid, threshold=100, callback=None, stop_on_double_spend=False):
	'''Estimate a transaction's propagation across the STRAKS network
		Returns a tuple consisting of:
		* The percentage of explorers that are aware of the txid;
		* The transaction's double spend status.

		Keyword arguments:
		txid       The txid to query
		threshold  A percentage at which the propagation check is considered finished
		callback   A function which will be called after every explorer query
				The function will be called with the perliminary results
		stop_on_double_spend
				The check will be aborted as soon as a double spend is detected
		'''
	sightings = 0
	double_spend = False
	for server in explorers.copy():
		try:
			tx = TxInfo(txid, explorer=server['name'])
		except TxNotFoundError:
			continue
		except KeyboardInterrupt:
			raise
		except:
			exception = sys.exc_info()[1]
			try:
				error = exception.reason
			except AttributeError:
				error = exception
			print('Could not fetch explorer data: {}'.format(error))
			continue
		if tx.double_spend:
			double_spend = True
		sightings += 1
		propagation = 100 * sightings / len(explorers)
		if callback is not None:
			callback(propagation, double_spend)
		if propagation >= threshold:
			break
		elif stop_on_double_spend:
			break
	return propagation, double_spend


NetworkValues = namedtuple('NetworkValues',
                           ('network_name', 'subnet_name', 'code', 'wif', 'address',
                            'pay_to_script', 'prv32', 'pub32'))

# TODO
def generate_address(xpub, idx, cash=True):
	'''Generate a bitcoin cash or bitcoin legacy address from the extended public key at the given index'''
	# Optional dependencies if unused
	from pycoin.ui.key_from_text import key_from_text
	from pycoin.networks.registry import network_for_netcode
	from pycoin.networks.all import _transform_NetworkValues_to_Network
	from pycoin.serialize import h2b
	stak_network_tuple = NetworkValues("STRAKS", "mainnet", "STAK", b'\xcc', b'\x3f', b'\x05', h2b('0488aDe4'), h2b('0488b21e'))
	stak_network = _transform_NetworkValues_to_Network(stak_network_tuple)

	#stak_network = network_for_netcode('STAK') 
	subkey = key_from_text(xpub, networks=[stak_network]).subkey(0).subkey(idx)

	return subkey.address()


def validate_key(key):
	'''Check the validity of a key or an address'''
	# Optional dependencies if unused
	from pycoin.ui.key_from_text import key_from_text
	from pycoin.networks.all import _transform_NetworkValues_to_Network
	from pycoin.serialize import h2b
	stak_network_tuple = NetworkValues("STRAKS", "mainnet", "STAK", b'\xcc', b'\x3f', b'\x05', h2b('0488aDe4'), h2b('0488b21e'))
	stak_network = _transform_NetworkValues_to_Network(stak_network_tuple)
	if key[0] in 'S' or key[0:4] in 'xpub':
		if not key_from_text(key):
				return False
		else:
			return True
	

def convert_address(address):

	'''Convert an address back and forth between cash and legacy formats'''
	return address



if __name__ == '__main__':
	print('===== Known block explorers =====')
	for server in explorers:
		print(server['name'])
	try:
		cur = sys.argv[1].upper()
		print('\n===== Known exchange rate sources with {cur} support ====='.format(cur=cur))
	except IndexError:
		print('\n===== Known exchange rate sources =====')
	for server in exchanges:
		support = True
		try:
			get_price(cur, exchange=server['name'])
		except (KeyError, ValueError, urllib.error.HTTPError):
			error = sys.exc_info()[1]
			try:
				error = error.reason
			except AttributeError:
				pass
			if isinstance(error, KeyError):
				error = 'Key error: ' + str(error)
			print('{src} does not provide {cur} exchange rate: {error}'.format(src=server['name'], cur=cur, error=error))
			support = False
		except KeyboardInterrupt:
			sys.exit()
		except NameError:
			pass
		if support:
			print(server['name'])
