# -*- coding: utf-8 -*-
from gabrielfalcao_httpbin.client import HttpBinClient


def entrypoint():
    client = HttpBinClient()
    print("your ip is: {}".format(client.ip()))


if __name__ == '__main__':
    entrypoint()
