import signal
import argparse
from twisted.internet import reactor, defer
from orchstr8.services import BaseLbryServiceStack, LbryServiceStack


@defer.inlineCallbacks
def start_stack(stack):
    yield stack.startup()
    stack.lbrycrd.print_info()
    stack.lbryumserver.print_info()
    if isinstance(stack, LbryServiceStack):
        stack.lbry.print_info()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--full-stack', action="store_true")
    args = parser.parse_args()
    if args.full_stack:
        stack = LbryServiceStack(True)
    else:
        stack = BaseLbryServiceStack(True)
    start_stack(stack)
    reactor.addSystemEventTrigger('before', 'shutdown', stack.shutdown)
    signal.signal(signal.SIGINT, lambda *a: reactor.stop())
    reactor.run()
