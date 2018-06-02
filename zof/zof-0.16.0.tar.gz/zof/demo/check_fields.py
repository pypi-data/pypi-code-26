import zof
import yaml


APP = zof.Application('check_fields')


@APP.bind()
class CheckFields:

    def __init__(self):
        self.test_fields = yaml.load(TEST_FIELDS)

    @APP.message('channel_up')
    async def channel_up(self, event):
        dp = event['datapath']
        result = []
        for field_name in self.test_fields:
            result.append(await self._test_field(dp, field_name))
        print(result)

    async def _test_field(self, dp, field_name):
        field = self.test_fields[field_name]
        match = field['match'].copy()
        instructions = field.get('instructions')
        prereq_name = field.get('prereq')

        prereq = self.test_fields[prereq_name] if prereq_name else None
        while prereq:
            match.extend(prereq['match'])
            prereq = prereq.get('prereq')
        if await self._send_flowmod(dp, match, instructions):
            return { 'field': field_name }

    async def _send_flowmod(self, dp, match, instructions):
        dp.send_msg(self._flowmod(match, instructions))

        return True

    @staticmethod
    def _flowmod(match, instructions):
        return {
            'type': 'FLOW_MOD',
            'msg': {
                'table_id': 0,
                'command': 'ADD',
                'priority': 15000,
                'match': match,
                'instructions': instructions
            }
        }


TEST_FIELDS = '''
#eth_dst:
#  match:
#    - field: ETH_DST
#      value: '00:00:00:00:00:01'

_ipv4:
  match:
    - field: ETH_TYPE
      value: 0x0800

tcp_flags_v4:
  prereq: _ipv4
  match:
    - field: TCP_FLAGS
      value: 80

mpls_label:
  match: 
    - field: ETH_TYPE
      value: 0x8847
    - field: MPLS_LABEL
      value: 0x0fffff

mpls_label_test:
  match: []
  instructions:
    - instruction: APPLY_ACTIONS
      actions: 
        - action: PUSH_VLAN
          ethertype: 0x8100
        - action: SET_FIELD
          field: VLAN_VID
          value: 0x1001
        #- action: PUSH_VLAN
        #  ethertype: 0x88A8
        #- action: SET_FIELD
        #  field: VLAN_VID
        #  value: 0x1002
        - action: PUSH_MPLS
          ethertype: 0x8847
        - action: SET_FIELD
          field: MPLS_LABEL
          value: 0xabcd
        - action: SET_MPLS_TTL
          ttl: 0x0900
        - action: PUSH_MPLS
          ethertype: 0x8847
        - action: SET_FIELD
          field: MPLS_LABEL
          value: 0xcdef
        - action: SET_MPLS_TTL
          ttl: 0x0A00
        - action: OUTPUT
          port_no: CONTROLLER


pkt_reg0:
  match:
    - field: PKT_REG0
      value: 0

sctp_src:
  prereq: _ipv4
  match:
    - field: SCTP_SRC
      value: 80


vlan_vid:
  match:
    - field: VLAN_VID
      value: 0x1000

'''


if __name__ == '__main__':
    zof.run()

