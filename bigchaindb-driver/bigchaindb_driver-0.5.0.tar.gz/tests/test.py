from time import sleep
from uuid import uuid4
from pprint import pprint

import requests

from bigchaindb_driver import BigchainDB
from bigchaindb_driver.crypto import generate_keypair

BDB_URL = 'http://bigchaindb:9984'
TX_URL = BDB_URL + '/api/v1/transactions/'
OP_URL = BDB_URL + '/api/v1/outputs?public_key='

bdb = BigchainDB(BDB_URL)

alice, bob, carly = generate_keypair(), generate_keypair(), generate_keypair()

print('Alice creates her asset')
tx1 = bdb.transactions.prepare(
    operation='CREATE',
    signers=alice.public_key,
    asset={'data': {'x': str(uuid4())}})
ff1 = bdb.transactions.fulfill(tx1, private_keys=alice.private_key)
bdb.transactions.send(ff1)
pprint(ff1)
sleep(2)
assert requests.get(TX_URL + ff1['id']).status_code == 200

# trigger the 'fastquery' error
# return fastquery.FastQuery(self.connection, self.me)
# TypeError: object() takes no parameters
# print(requests.get(OP_URL + alice.public_key))

print('Alice transfers her asset to Bob')
tx2 = bdb.transactions.prepare(
    operation='TRANSFER',
    asset={'id': ff1['id']},
    metadata={'foo': 'bar'},
    inputs={
        'fulfillment': ff1['outputs'][0]['condition']['details'],
        'fulfills': {
            'output_index': 0,
            'transaction_id': ff1['id']
            },
        'owners_before': ff1['outputs'][0]['public_keys']
    },
    recipients=bob.public_key)

ff2 = bdb.transactions.fulfill(tx2, private_keys=alice.private_key)
bdb.transactions.send(ff2)
pprint(ff2)
sleep(2)
print(requests.get(TX_URL + ff2['id']).status_code)

print('Bob transfers his asset to Carly')
tx3 = bdb.transactions.prepare(
    operation='TRANSFER',
    asset={'id': ff1['id']},
    metadata={'foo': 'bar'},
    inputs={
        'fulfillment': ff2['outputs'][0]['condition']['details'],
        'fulfills': {
            'output_index': 0,
            'transaction_id': ff2['id']
            },
        'owners_before': ff2['outputs'][0]['public_keys']
    },
    recipients=carly.public_key)

ff3 = bdb.transactions.fulfill(tx3, private_keys=bob.private_key)
bdb.transactions.send(ff3)
pprint(ff3)
sleep(2)
print(requests.get(TX_URL + ff3['id']).status_code)

