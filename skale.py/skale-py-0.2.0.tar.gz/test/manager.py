from unittest import TestCase
from skale import Skale, NodeManager, Token, BaseContract
import unittest


class ManagerContractTest(TestCase):
    def setUp(self):
        self.skale = Skale('51.0.1.99', 8546)

    def test_create_node(self):
        pass
        # todo: create node and save config here

    def test_get_node(self):
        node_id = 11 # todo: get node_id from the config
        node = self.skale.manager().get_node(node_id)
        print(node)
        # todo: add check



if __name__ == '__main__':
    unittest.main()
