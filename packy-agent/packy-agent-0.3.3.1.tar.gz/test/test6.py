import socket

from packy_agent.modules.base.socket import send_icmp_probe
from packy_agent.modules.traceroute.methods.icmp import receive_icmp_reply

icmp = socket.getprotobyname('icmp')
raw_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
raw_socket.setsockopt(socket.SOL_IP, socket.IP_TTL, 1)

# send_icmp_probe(raw_socket, '192.168.1.1', 0x0F0F, payload='1234'.decode('hex'))
# rtt = receive_icmp_reply(raw_socket, 0x0F0F, 10)
send_icmp_probe(raw_socket, '8.8.8.8', 0x0F0F, payload='1234'.decode('hex'))
rtt = receive_icmp_reply(raw_socket, 0x0F0F, 10)

print 'RTT:', rtt
