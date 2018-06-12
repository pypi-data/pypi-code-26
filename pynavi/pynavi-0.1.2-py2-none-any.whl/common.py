# -*- coding: utf-8 -*-
# Author: sunguangran (sunguangran@daixiaomi.com)
import socket


def get_local_ip():
    """
    获取本地IP地址
    :return:
    """
    s = None
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 53))
        return s.getsockname()[0]
    except Exception as e:
        raise e
    finally:
        if s:
            s.close()
