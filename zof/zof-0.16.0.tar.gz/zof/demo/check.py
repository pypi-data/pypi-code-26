import zof
import asyncio

APP = zof.Application('check')

CMDS = [ 
    'type: GET_CONFIG_REQUEST',
    'type: GET_ASYNC_REQUEST',
    'type: REQUEST.DESC',
    'type: REQUEST.TABLE',
    '''
    type: REQUEST.GROUP
    msg:
      group_id: ALL
    ''',
    '''
    type: REQUEST.FLOW
    msg:
      table_id: ALL
      out_port: ANY
      out_group: ANY
      cookie: 0
      cookie_mask: 0
      match: []
    ''',
    '''
    type: REQUEST.AGGREGATE
    msg:
      table_id: ALL
      out_port: ANY
      out_group: ANY
      cookie: 0
      cookie_mask: 0
      match: []      
    ''',
    '''
    type: REQUEST.METER
    msg:
      meter_id: ALL
    ''',
    'type: REQUEST.TABLE_FEATURES',
    '''
    type: ROLE_REQUEST
    msg:
      role: ROLE_NOCHANGE
      generation_id: 0
    ''',
    'type: REQUEST.QUEUE',
    'type: REQUEST.QUEUE_DESC',
    'type: REQUEST.GROUP_DESC',
    'type: REQUEST.TABLE_DESC'
]

@APP.message('channel_up')
async def channel_up(event):
    for cmd in CMDS:
        APP.logger.info('Send %s', cmd)
        try:
            result = await zof.compile(cmd).request()
            print(result)
        except zof.exception.ControllerException as ex:
            APP.logger.error(ex)

    await test_flowmods()


FIELDS = {
    'eth_dst': ('00:00:00:00:00:01', 0x0800),
    'eth_src': ('00:00:00:00:00:02', 0x0800),
    'tcp_flags': (0, 0x0800),
    'nx_tcp_flags': (0, 0x0800),
    'pkt_reg0': (0, 0x0800), 
    'mpls_label': (0, 0x8847),
    'sctp_src': (1, 0x0800)
}

def flowmod(ethtype, field, value):
    return '''
    type: FLOW_MOD
    msg:
      table_id: 0
      command: ADD
      match: 
        - field: ETH_TYPE
          value: %s
        - field: '%s'
          value: '%s'
    ''' % (ethtype, field.upper(), value)

async def test_flowmods():
    for field, (value, ethtype) in FIELDS.items():
        APP.logger.info("Test %s", field)
        zof.compile(flowmod(ethtype, field, value)).send()
        await asyncio.sleep(1)


if __name__ == '__main__':
    zof.run()
