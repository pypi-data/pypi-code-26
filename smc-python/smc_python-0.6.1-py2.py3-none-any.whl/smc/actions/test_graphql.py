'''
Created on May 18, 2018

@author: davidlepage
'''
from pprint import pprint


query = '''
query meta
{
  meta
  {
    schema
  }
}
'''

if __name__ == '__main__':
    import ptf.gql.smc as smc
    S = smc.SMC()
    pprint(vars(S))
    pprint(vars(S.config))
    #S.config.set_gql_ip(gql_ip='172.18.1.151')
    pprint(vars(S.control))
    