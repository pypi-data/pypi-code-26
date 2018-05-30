import threading
import logging
import socket
import json
from argparse import Namespace

try:
    import ssl
except Exception as e:
    print("Python failed to import ssl package, hope you won't need it")
import sys
import re
import os

import aoet.proxy.http as http
import aoet
from aoet import logger

host_re = re.compile(b'(Host:\ )(.+)$', re.MULTILINE)
location_re = re.compile(b'(Location:\ )(.+)$', re.MULTILINE)


class Splitter:
    def __init__(self, args):
        self.prd = args.prd
        self.tst = args.tst
        self.prd_port = args.prd_port
        self.tst_port = args.tst_port

        self.port = args.port
        self.container = ResponsesContainer(args.out)

        self.buffer_size = args.buffer_size

        self._should_shutdown = False

    def start(self):
        i = 0
        logger.info("Starting listening for incoming traffic on port " + str(self.port))
        logger.info("Splitting traffic between {}:{} and {}:{}".format(self.prd, self.prd_port, self.tst, self.tst_port))
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
            s.bind(('localhost', self.port))
            s.listen(0)
        except Exception as e:
            logger.exception("Error during initializing connection", e)
            sys.exit(2)

        logger.info("Server is ready to accept connections")

        self._should_shutdown = False

        try:
            while not self._should_shutdown:
                try:
                    conn, addr = s.accept()
                except socket.timeout:
                    continue

                data = conn.recv(self.buffer_size)
                full_request = data
                req = http.HttpRequest.from_socket(i, data)

                while req.remaining_bytes > 0:
                    data = conn.recv(self.buffer_size)
                    full_request += data
                    req.append_data(data)

                self.container.append_request(req)
                threading.Thread(target=self._forward,
                                 args=(i,
                                       self.prd,
                                       self.prd_port,
                                       self._replace_host(full_request, self.prd.encode('utf-8')),
                                       conn)
                                 ).start()
                threading.Thread(target=self._forward,
                                 args=(i,
                                       self.tst,
                                       self.tst_port,
                                       self._replace_host(full_request, self.tst.encode('utf-8')))
                                 ).start()
                i += 1
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received, shutting down")
            sys.exit(0)
        except Exception as e:
            logger.exception(e)
            sys.exit(2)
        finally:
            logger.info("Finally")
            s.close()
            self.container.save()

    def stop(self):
        self._should_shutdown = True

    def _forward(self, ind, dest, port, data, conn=None):
        s = None
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            logger.debug('Connecting to %s %s' % (str(dest), str(port)))
            s.connect((dest, port))
            if port == 443:
                s = ssl.wrap_socket(s, keyfile=None, certfile=None, server_side=False, cert_reqs=ssl.CERT_NONE)
            s.settimeout(5)
            s.sendall(data)
            response = None
            while response is None or response.remaining_bytes > 0:
                reply = s.recv(self.buffer_size)
                if len(reply) > 0:
                    if response is None:
                        response = http.HttpResponse.from_socket(ind, reply)
                    else:
                        response.append_data(reply)
                    if conn is not None:
                        conn.send(reply)
            s.close()

            if conn is not None:
                self.container.append_prd_response(response)
                conn.close()
            else:
                self.container.append_tst_response(response)
        except socket.timeout:
            if conn is not None:
                logging.warning("Timeout in PRD thread")
                self.container.append_prd_response(http.HttpResponse.timeout(ind))
                conn.close()
            else:
                logger.warning("Timeout in TST thread")
                self.container.append_tst_response(http.HttpResponse.timeout(ind))
        except Exception as e:
            logger.exception(e)
            if conn is not None:
                conn.close()
            s.close()
            sys.exit(1)

    def _replace_host(self, req, repl):
        global host_re
        return host_re.sub(b'Host: ' + repl + b'\r', req)

    def _replace_location(self, req, repl):
        global location_re
        return location_re.sub(b'Location: ' + repl + b'\r', req)


class ResponsesContainer:
    def __init__(self, out):
        self._prd_resp = []
        self._tst_resp = []
        self._reqs = []
        self._out = out
        if not os.path.exists(out):
            os.makedirs(out)

    def append_request(self, req):
        self._reqs.append(req)

    def append_prd_response(self, resp):
        self._prd_resp.append(resp)

    def append_tst_response(self, resp):
        self._tst_resp.append(resp)

    def save(self):
        self._reqs = list(map(http.HttpRequest.to_dict, sorted(self._reqs, key=lambda a: a.ind)))
        self._prd_resp = list(map(http.HttpResponse.to_dict, sorted(self._prd_resp, key=lambda a: a.ind)))
        self._tst_resp = list(map(http.HttpResponse.to_dict, sorted(self._tst_resp, key=lambda a: a.ind)))

        # self.validate()
        logger.info("Saving {} requests and {} prd and {} tst responses.".format(len(self._reqs), len(self._prd_resp), len(self._tst_resp)))

        with open(os.path.join(self._out, aoet.REQUESTS_FILE), 'w') as fp:
            json.dump(self._reqs, fp)
        with open(os.path.join(self._out, aoet.PRD_FILE), 'w') as fp:
            json.dump(self._prd_resp, fp)
        with open(os.path.join(self._out, aoet.TST_FILE), 'w') as fp:
            json.dump(self._tst_resp, fp)

    @staticmethod
    def load(folder):
        with open(os.path.abspath(os.path.join(folder, aoet.REQUESTS_FILE))) as fp:
            j = json.load(fp)
            requests = list(map(http.HttpRequest.from_json, j))
        with open(os.path.join(folder, aoet.PRD_FILE)) as fp:
            j = json.load(fp)
            prd = list(map(http.HttpResponse.from_json, j))
        with open(os.path.join(folder, aoet.TST_FILE)) as fp:
            j = json.load(fp)
            tst = list(map(http.HttpResponse.from_json, j))
        return requests, prd, tst


def start(arguments):
    s = Splitter(arguments)
    s.start()


def add_subparsers(subparsers):
    parser_split = subparsers.add_parser('splitter', help='Forking Traffic Splitter')

    parser_split.add_argument('--prd',      dest='prd',      type=str, required=True, help='PRD server address')
    parser_split.add_argument('--prd-port', dest='prd_port', type=int, required=True, help='PRD server port')
    parser_split.add_argument('--tst',      dest='tst',      type=str, required=True, help='TST server address')
    parser_split.add_argument('--tst-port', dest='tst_port', type=int, required=True, help='TST server port')

    parser_split.add_argument('--port', '-p', dest='port', type=int, help='Proxy listening port', default=8080)
    parser_split.add_argument('--out', '-o',  dest='out',  type=str, help='Output directory', default='./out')

    parser_split.add_argument('--buffer-size', dest='buffer_size', type=int, default=4096, help='Buffer size')
    parser_split.set_defaults(func=start)


if __name__ == '__main__':
    n = Namespace()
    n.port = 8080
    n.buffer_size = 4096
    n.prd = 'acer_filestorage'
    n.prd_port = 8080
    n.tst = 'acer_filestorage'
    n.tst_port = 8081
    n.out = 'data/tmp'
    print("Starting with default config")
    start(n)
