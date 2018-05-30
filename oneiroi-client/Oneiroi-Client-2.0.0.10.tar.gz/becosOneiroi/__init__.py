root.attrib['name']
root.attrib['soureClient']
root.attrib['sendFrom']
root.attrib['targetClient']

from msg import msg
nmsg=msg()
nmsg.name='msg'
nmsg.sendFrom='testnode'
nmsg.sendTo='testnode'
nmsg.msgat='sdfsdfs'
nmsg.msgat2='sdfsdfsdfsd'
from testnode_Impl1 import testnode_Impl
anode=testnode_Impl()
anode.send_msg(nmsg)

