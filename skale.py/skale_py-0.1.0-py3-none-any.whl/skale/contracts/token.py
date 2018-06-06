from skale.contracts import BaseContract
import skale.utils.helper as Helper

class Token(BaseContract):
  def __init__(self, skale):
    name = 'token'
    super().__init__(skale, name, skale.abi[f'{name}_address'], skale.abi[f'{name}_abi'] )
