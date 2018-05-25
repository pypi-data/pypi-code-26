# -*- coding: UTF-8 -*-
"""
 File Name :    ./format.py
 Author :       unasm
 mail :         unasm@sina.cn
 Last_Modified: 2018-05-15 18:49:02
"""
from datetime import datetime
import pytz
import json

class LogFormat(object):
    """
        日志的全部支持字段对象
    """
    # 时区

    TimeFormat = ["%Y-%m-%dT%H:%M:%S.%f",
                  "%Y-%m-%d %H:%M:%S.%f",
                  "%Y-%m-%d %H:%M:%S",
                  "%Y-%m-%dT%H:%M:%S",
                  "%Y-%m-%dT%H:%M:%S +08:00",
                  "%Y-%m-%dT%H:%M:%S+08:00",
                  "%Y-%m-%dT%H:%M:%S+0800",
                  "%Y-%m-%dT%H:%M:%S +0800",
                  "%Y-%m-%dT%H:%M:%S.%f+08:00",
                  "%Y-%m-%dT%H:%M:%S.%f+0800",
                  "%Y-%m-%dT%H:%M:%S.%f +0800",
                  "%Y-%m-%dT%H:%M:%S.%f +08:00",
                  "%Y-%m-%d %H:%M:%S.%f Z",
                  "%Y-%m-%d %H:%M:%S.%fZ",
                  "%Y-%m-%dT%H:%M:%S.%f Z",
                  "%Y-%m-%dT%H:%M:%S.%fZ"]

    TZ = pytz.timezone("Asia/Shanghai")
    def setProject(self, project):
        self.project = project

    def setModule(self, module):
        self.module = module

    def _processTime(self, time):
        if isinstance(time, (datetime)):
            time = LogFormat.TZ.localize(time)
        elif isinstance(time, (float)):
            dt = datetime.fromtimestamp(time)
            time = LogFormat.TZ.localize(dt)
        else:
            flag = False
            for dformat in LogFormat.TimeFormat:
                try:
                    date = datetime.strftime(time, dformat)
                    if date != 0:
                        time = LogFormat.TZ.localize(date)
                        flag = True
                        break
                except ValueError:
                    continue
            if flag is False:
                raise Exception("时间格式异常")
        return time.isoformat("T")

    def setVersion(self, version):
        self.version = version

    def setLevel(self, level):
        self.level = level.lower()

    def setBeginTime(self, beginTime):
        self.beginTime = self._processTime(beginTime)

    def setEndTime(self, endTime):
        self.endTime = self._processTime(endTime)

    def setMethodURI(self, methodURI):
        self.methodURI = methodURI

    def setUserId(self, userId):
        self.userId = userId

    def setUser(self, user):
        self.user = user

    def setEventName(self, eventName):
        self.eventName = eventName

    def setContextId(self, contextId):
        self.contextId = contextId

    def setProductId(self, productId):
        self.productId = productId

    def setSessionId(self, sessionId):
        self.sessionId = sessionId

    def setOriginId(self, originId):
        self.originId = originId

    def setClient_name(self, client_name):
        self.client_name = client_name

    def setServiceName(self, serviceName):
        self.serviceName = serviceName

    def setCallerClass(self, callerClass):
        self.callerClass = callerClass

    def setCallerMethod(self, callerMethod):
        self.callerMethod = callerMethod

    def setCallerLine(self, callerLine):
        self.callerLine = callerLine

    def setLoginTime(self, logTime):
        self.logTime = self._processTime(logTime)

    def setTraceSystemId(self, traceSystemId):
        """
        请求的系统id
        :param traceSystemId: 
        :return: 
        """
        self.traceSystemId = traceSystemId

    def setTraceParentSystemId(self, traceParentSystemId):
        self.traceParentSystemId = traceParentSystemId

    def setRecordId(self, recordId):
        self.recordId = recordId

    def setMessage(self, message):
        self.message = message

    def setHost(self, host):
        self.host = host
    def setIp(self, ip):
        self.ip = ip

    def __str__(self):
        return json.dumps(self.__dict__, ensure_ascii=False)
