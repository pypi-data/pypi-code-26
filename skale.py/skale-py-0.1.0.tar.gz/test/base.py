from unittest import TestCase
from skale import Skale, NodeManager, Token, BaseContract
import unittest


class Web3Test(TestCase):
    def setUp(self):
        self.skale = Skale('51.0.1.99', 8546)

    def test_connection(self):
        self.assertTrue(self.skale.web3.isConnected(), 'not connected to node')

    def test_contracts_instances(self):
        manager_contract = self.skale.manager()
        self.assertIsInstance(manager_contract, NodeManager)

        token_contract = self.skale.token()
        self.assertIsInstance(token_contract, Token)

        self.assertIsInstance(token_contract, BaseContract)
        self.assertIsInstance(manager_contract, BaseContract)


if __name__ == '__main__':
    unittest.main()
