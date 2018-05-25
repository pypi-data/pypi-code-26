# -*- coding: UTF-8 -*-
"""
 File Name :    ab.py
 Author :       unasm
 mail :         unasm@sina.cn
 Last_Modified: 2018-05-14 21:40:35
"""

import logging
import os
import uuid
import socket
import json
import time
from aispeech_logger.logformat import LogFormat

import flask
from flask import _app_ctx_stack
from flask import current_app
from flask import g
from flask import request
from py_zipkin import zipkin
from kafka import SimpleProducer, SimpleClient
#from kafka import SimpleProducer, KafkaClient


__version_info__ = ('0', '0', '4')
__version__ = '.'.join(__version_info__)
__author__ = 'killpanda/unasm'
__license__ = 'BSD'
__copyright__ = '(c) 2016 by killpanda'
__all__ = ['Tracer', "Formatter"]


def get_ip_address():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip

#def get_ip_address(ifname):
#    try:
#        sct = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#        return socket.inet_ntoa(fcntl.ioctl(
#            sct.fileno(),
#            0x8915,  # SIOCGIFADDR
#            struct.pack('256s', ifname[:15])
#        )[20:24])
#    except Exception as ex:
#        return ''

class BaLogHandler(logging.Handler):
    """
        写入数据
        写入到kafka，格式化的
    """

    def __init__(self, kafka_addr=None, topic=None, module=None, project=None):
        """
        初始化 handler
        :param kafka_addr:  kafka的地址 和端口，默认并不需要，优先读取环境变量的信息，如果没有的话，则使用kafka_addr
        :param topic: 消费的kafka 端口
        """
        logging.Handler.__init__(self)
        if "HIS_KAFKA_HOST" in os.environ and "HIS_KAFKA_PORT" in os.environ:
            kafka_addr = "%s:%s" % (os.environ["HIS_KAFKA_HOST"], os.environ["HIS_KAFKA_PORT"])
        elif kafka_addr is None:
            raise Exception("请传递kafka_addr，或者配置环境变量HIS_KAFKA_HOST, HIS_KAFKA_PORT")

        if "LOG_KAFKA_TOPIC_ONLINE" in os.environ:
            topic = os.environ["LOG_KAFKA_TOPIC_ONLINE"]
        elif topic is None:
            raise Exception("请配置topic")

        kafka_client = SimpleClient(kafka_addr)
        self.producer = SimpleProducer(kafka_client, async=True, batch_send_every_n=20, batch_send_every_t=60)
        # todo 优化下这里, 跟tracer一起配置
        host_ip = get_ip_address()
        host = socket.gethostname()
        self.module = module
        self.project = project
        formatter = Formatter(module=self.module, project=self.project, version="v0.1", host=host, ip=host_ip)
        self.kafka_topic_name = topic
        self.formatter = formatter
        #self.producer = KafkaProducer(bootstrap_servers=hosts_list,api_version=(0,10,1))

    def emit(self, record):
        try:
            formatted_msg = self.format(record)
            #异步处理
            self.producer.send_messages(self.kafka_topic_name, formatted_msg.encode('utf-8'))
            # produce message
            #self.producer.send(self.kafka_topic_name, msg.encode("utf-8"))
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)

    def close(self):
        #self.producer.stop()
        logging.Handler.close(self)

class Formatter(object):
    converter = time.localtime
    def __init__(self, module, project, version=None, host=None, ip=None):
        """
        Initialize the formatter with specified format strings.

        Initialize the formatter either with the specified format string, or a
        default as described above. Allow for specialized date formatting with
        the optional datefmt argument (if omitted, you get the ISO8601 format).

        Use a style parameter of '%', '{' or '$' to specify that you want to
        use one of %-formatting, :meth:`str.format` (``{}``) formatting or
        :class:`string.Template` formatting in your format string.

        .. versionchanged:: 3.2
           Added the ``style`` parameter.
        """
        self.module = module
        self.project = project
        if "IMAGE_VERSION" in os.environ:
            self.version = os.environ["IMAGE_VERSION"]
        elif version is not None:
            self.version = version
        if ip is None:
            self.ip = get_ip_address()
        else:
            self.ip = ip

        if host is None:
            self.host = socket.gethostname()
        else:
            self.host = host

    def _processPublicFields(self, log_format, record):
        """
            处理 系统 级别的公共字段
            todo    加上 host 和 ip
            :param log_format
            :param record
            :return
        """
        log_format.setProject(self.project)
        log_format.setModule(self.module)
        log_format.setLevel(record.levelname)
        if hasattr(self, "version") and self.version is not None:
            log_format.setVersion(self.version)

        if hasattr(record, "funcName") and record.funcName is not None:
            log_format.setCallerMethod(record.funcName)
        if hasattr(record, "lineno") and record.lineno is not None:
            log_format.setCallerLine(record.lineno)

        if hasattr(record, "filename") and record.filename is not None:
            log_format.setCallerClass(record.filename)
        if self.host is not None:
            log_format.setHost(self.host)
        if self.ip is not None:
            log_format.setIp(self.ip)

        if hasattr(g, "_zipkin_span"):
            # 如果有调用链追踪的信息，其实没有的话，也应该加起来的, 这样才能将线上 离线脚本的日志串联
            #print(g._zipkin_span.zipkin_attrs)
            attrs = g._zipkin_span.zipkin_attrs
            if hasattr(attrs, "trace_id") and attrs.trace_id is not None:
                log_format.setRecordId(attrs.trace_id)
            if hasattr(attrs, "span_id") and attrs.span_id is not None:
                log_format.setTraceSystemId(attrs.span_id)
            if hasattr(attrs, "parent_span_id") and attrs.parent_span_id is not None:
                log_format.setTraceParentSystemId(attrs.parent_span_id)

    #def _processInputDict(self, log_format, json_dict):
    def _process_input_dict(self, log_format, json_dict):
        """
        处理 dict 中的日志字段, 仅仅处理用户系统有权限处理的
        :param log_format:  本次要处理的日志
        :param json_dict:   用户提供的信息
        :return: 
        """
        if "methodURI" in json_dict:
            log_format.setMethodURI(json_dict["methodURI"])
        if "beginTime" in json_dict:
            log_format.setBeginTime(json_dict["beginTime"])
        if "endTime" in json_dict:
            log_format.setEndTime(json_dict["endTime"])
        if "userId" in json_dict:
            log_format.setUserId(json_dict["userId"])
        if "user" in json_dict:
            log_format.setUserId(json_dict["user"])
        if "eventName" in json_dict:
            log_format.setEventName(json_dict["eventName"])
        if "recordId" in json_dict:
            log_format.setRecordId(json_dict["recordId"])
        if "originId" in json_dict:
            log_format.setOriginId(json_dict["originId"])
        if "productId" in json_dict:
            log_format.setProductId(json_dict["productId"])
        if "contextId" in json_dict:
            log_format.setContextId(json_dict["contextId"])
        if "serviceName" in json_dict:
            log_format.setServiceName(json_dict["serviceName"])
        if "client_name" in json_dict:
            log_format.setClient_name(json_dict["client_name"])
        if "message" in json_dict:
            log_format.setMessage(json_dict["message"])


    def format(self, record):
        """
        支持 logger 的 五种写法, 
        1, object,
        2, 词典
        3, eventName, message
        4, json str
        5, string 为message
        """
        log_format = LogFormat()
        log_format.setLoginTime(record.created)
        self._processPublicFields(log_format, record)
        if hasattr(record, "args") and len(record.args):
            log_format.setEventName(record.getMessage())
            log_format.setMessage(record.args)
        else:
            json_dict = {}
            if isinstance(record.msg, (str)):
                # 如果传入的是json string
                try:
                    json_dict = json.loads(record.msg)
                except ValueError:
                    msg = record.getMessage()
                    log_format.setMessage(msg)
            else:
                # 如果传入的是对象
                if hasattr(record.msg, "__dict__"):
                    json_dict = record.msg.__dict__
                elif isinstance(record.msg, (dict)):
                    json_dict = record.msg
                else:
                    raise Exception("日志模块异常，不常见的写入日志方式")
            self._process_input_dict(log_format, json_dict)
        return log_format.__str__()

class Tracer(object):
    """
        添加调用链追踪的信息
    """
    @staticmethod
    def _gen_random_id():
        """
            生成recordId
        """
        return str(uuid.uuid1().int)[:32]
        #return ''.join(
        #    random.choice(
        #        string.digits) for i in range(16))

    def _gen_span_id(self, parent_id=None):
        """
            生成系统id，要求有一定的规律，不是随机的，
                而是能体现层级关系，且稳定的，生成的
            module-(parent_id + 1)
        """
        return "%s->1" % (parent_id)

    def __init__(self,
                 app=None,
                 sample_rate=100,
                 timeout=1):
        self._exempt_views = set()
        self._sample_rate = sample_rate
        if app is not None:
            self.init_app(app)
        self._transport_handler = None
        self._transport_exception_handler = None
        self._timeout = timeout

    def default_exception_handler(self, ex):
        """
            异常处理
        """
        pass

    def get_dict(self, value):
        """
        将一个对象，多层级结构的，转换为 dict
        :param value: 
        :return: 
        """
        res_dict = {}
        dict_decode = value.__dict__
        for key in dict_decode:
            if dict_decode[key] is None:
                res_dict[key] = None
            elif isinstance(dict_decode[key], (int, bool, str)):
                res_dict[key] = dict_decode[key]
            elif isinstance(dict_decode[key], (list)):
                array = []
                for sub_key in dict_decode[key]:
                    array.append(self.get_dict(sub_key))
                res_dict[key] = array
            else:
                sub_dict = self.get_dict(dict_decode[key])
                res_dict[key] = sub_dict
        return res_dict.copy()


    def default_handler(self, encoded_span):
        """
            调用链追踪的日志日志处理
            默认走 环境变量
            需要调整格式，保证与java的统一
        """
        #try:
        #    #msgs = []
        #    #for span in encoded_span:
        #    #    res_dict = self.get_dict(span)
        #    #    msgs.append(res_dict)
        #    #json_str = json.dumps(msgs)
        #    #kafka_client = KafkaClient('{}:{}'.format('47.96.4.198', 9092))
        #    #producer = SimpleProducer(kafka_client)
        #    #producer.send_messages('zipkin', json_str)
        #    #body = str.encode('\x0c\x00\x00\x00\x01') + encoded_span
        #    #return requests.post(
        #    #    self.app.config.get('ZIPKIN_DSN'),
        #    #    data=encoded_span,
        #    #    headers={'Content-Type': 'application/x-thrift'},
        #    #    timeout=self._timeout,
        #    #)
        #except Exception as ex:
        #    #print("after_json_str_exception")
        #    #print(ex)
        #    if self._transport_exception_handler:
        #        self._transport_exception_handler(ex)
        #    else:
        #        self.default_exception_handler(ex)
        return None

    def transport_handler(self, callback):
        """
            todo     确认下
        """
        self._transport_handler = callback
        return callback

    def transport_exception_handler(self, callback):
        self._transport_exception_handler = callback
        return callback

    def init_app(self, app):
        self.app = app
        app.before_request(self._before_request)
        app.after_request(self._after_request)
        self._disable = app.config.get(
            'ZIPKIN_DISABLE', app.config.get('TESTING', False))
        return self

    def _should_use_token(self, view_func):
        return (view_func not in self._exempt_views)

    def _before_request(self):
        if self._disable:
            return

        _app_ctx_stack.top._view_func = \
            current_app.view_functions.get(request.endpoint)

        if not self._should_use_token(_app_ctx_stack.top._view_func):
            return
        headers = request.headers
        trace_id = headers.get('X-B3-TraceId') or Tracer._gen_random_id()
        parent_span_id = headers.get('X-B3-ParentSpanId')
        is_sampled = str(headers.get('X-B3-Sampled') or '0') == '1'
        # 这个是什么鬼 todo
        flags = headers.get('X-B3-Flags')

        zipkin_attrs = zipkin.ZipkinAttrs(
            trace_id=trace_id,
            parent_span_id=parent_span_id,
            span_id=self._gen_span_id(parent_span_id),
            flags=flags,
            is_sampled=is_sampled,
        )

        handler = self._transport_handler or self.default_handler

        span = zipkin.zipkin_span(
            service_name=self.app.name,
            span_name='{0}.{1}'.format(request.endpoint, request.method),
            transport_handler=handler,
            sample_rate=self._sample_rate,
            zipkin_attrs=zipkin_attrs,
            use_128bit_trace_id=True
        )
        g._zipkin_span = span
        g._zipkin_span.start()

    def exempt(self, view):
        view_location = '{0}.{1}'.format(view.__module__, view.__name__)
        self._exempt_views.add(view_location)
        return view

    def _after_request(self, response):
        if self._disable:
            return response
        if not hasattr(g, '_zipkin_span'):
            return response
        g._zipkin_span.stop()
        return response

    def create_http_headers_for_new_span(self):
        if self._disable:
            return dict()
        return zipkin.create_http_headers_for_new_span()

    @staticmethod
    def add_tag(key, value):
        if all([hasattr(g, '_zipkin_span'),
                g._zipkin_span,
                g._zipkin_span.logging_context]):
            dict_attr = {}
            dict_attr[key] = value
            g._zipkin_span.logging_context.binary_annotations_dict.update(dict_attr)
            #g._zipkin_span.logging_context.binary_annotations_dict.update(kwargs)

    @staticmethod
    def getTag(key):
        if all([hasattr(g, '_zipkin_span'),
                g._zipkin_span,
                g._zipkin_span.logging_context]):
            return g._zipkin_span.logging_context.binary_annotations_dict.get(key)

    @staticmethod
    def getRecordId():
        if hasattr(g, "_zipkin_span"):
            # 如果有调用链追踪的信息，其实没有的话，也应该加起来的, 这样才能将线上 离线脚本的日志串联
            #print(g._zipkin_span.zipkin_attrs)
            attrs = g._zipkin_span.zipkin_attrs
            if hasattr(attrs, "trace_id") and attrs.trace_id is not None:
                return attrs.trace_id
        return None





def child_span(func):
    def decorated(*args, **kwargs):
        span = zipkin.zipkin_span(
            service_name=flask.current_app.name,
            span_name=func.__name__,
        )
        kwargs['span'] = span
        with span:
            val = func(*args, **kwargs)
            span.update_binary_annotations({
                'function_args': args,
                'function_returns': val,
            })
            return val

    return decorated
