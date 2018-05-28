import logging

from packy_agent.modules.traceroute.methods.icmp import trace_hop_with_icmp

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)

# print trace_hop_with_icmp('192.168.1.1', 2, 1)
print trace_hop_with_icmp('10.10.10.20', 30, 100)
# print trace_hop_with_icmp('8.8.8.8', 2, 1)
# print trace_hop_with_icmp('8.8.8.8', 2, 100)
