import skale.utils.helper as Helper
from web3 import Web3, WebsocketProvider
import skale.contracts as contracts

class Skale:
  def __init__(self, ip, port, abi_filepath=None):
    ws_addr = Helper.generate_ws_addr(ip, port)
    self.web3 = Web3(WebsocketProvider(ws_addr))
    self.abi = Helper.get_abi(abi_filepath)
    self.__contracts = {}
    self.__init_contracts()

  def __init_contracts(self):
    self.add_contract('manager', contracts.NodeManager(self))
    self.add_contract('token', contracts.Token(self))

  def add_contract(self, name, skale_contract):
    self.__contracts[name] = skale_contract

  def get_contract_by_name(self, name):
    return self.__contracts[name]

  def manager(self):
    return self.get_contract_by_name('manager')

  def token(self):
    return self.get_contract_by_name('token')


