# -*- coding: utf-8 -*-
DESC = "cws-2018-03-12"
INFO = {
  "DescribeVuls": {
    "params": [
      {
        "name": "SiteId",
        "desc": "站点ID"
      },
      {
        "name": "MonitorId",
        "desc": "监控任务ID"
      },
      {
        "name": "Filters",
        "desc": "过滤条件"
      },
      {
        "name": "Offset",
        "desc": "偏移量，默认为0"
      },
      {
        "name": "Limit",
        "desc": "返回数量，默认为10，最大值为100"
      }
    ],
    "desc": "本接口 (DescribeVuls) 用于查询一个或多个漏洞的详细信息。"
  },
  "ModifyMonitorAttribute": {
    "params": [
      {
        "name": "MonitorId",
        "desc": "监测任务ID"
      },
      {
        "name": "Urls",
        "desc": "站点的url列表"
      },
      {
        "name": "Name",
        "desc": "任务名称"
      },
      {
        "name": "ScannerType",
        "desc": "扫描模式，normal-正常扫描；deep-深度扫描"
      },
      {
        "name": "Crontab",
        "desc": "扫描周期，单位小时，每X小时执行一次"
      },
      {
        "name": "RateLimit",
        "desc": "扫描速率限制，每秒发送X个HTTP请求"
      },
      {
        "name": "FirstScanStartTime",
        "desc": "首次扫描开始时间"
      },
      {
        "name": "MonitorStatus",
        "desc": "监测状态：1-监测中；2-暂停监测"
      }
    ],
    "desc": "本接口 (ModifyMonitorAttribute) 用于修改监测任务的属性。"
  },
  "CreateSitesScans": {
    "params": [
      {
        "name": "SiteIds",
        "desc": "站点的ID列表"
      },
      {
        "name": "ScannerType",
        "desc": "扫描模式，normal-正常扫描；deep-深度扫描"
      },
      {
        "name": "RateLimit",
        "desc": "扫描速率限制，每秒发送X个HTTP请求"
      }
    ],
    "desc": "本接口（CreateSitesScans）用于新增一个或多个站点的单次扫描任务。"
  },
  "DescribeConfig": {
    "params": [],
    "desc": "本接口 (DescribeConfig) 用于查询用户配置的详细信息。"
  },
  "CreateVulsMisinformation": {
    "params": [
      {
        "name": "VulIds",
        "desc": "漏洞ID列表"
      }
    ],
    "desc": "本接口（CreateVulsMisinformation）用于新增一个或多个漏洞误报信息。"
  },
  "CreateSites": {
    "params": [
      {
        "name": "Urls",
        "desc": "站点的url列表"
      }
    ],
    "desc": "本接口（CreateSites）用于新增一个或多个站点。"
  },
  "DescribeSites": {
    "params": [
      {
        "name": "SiteIds",
        "desc": "站点ID列表"
      },
      {
        "name": "Filters",
        "desc": "过滤条件"
      },
      {
        "name": "Offset",
        "desc": "偏移量，默认为0"
      },
      {
        "name": "Limit",
        "desc": "返回数量，默认为10，最大值为100"
      }
    ],
    "desc": "本接口 (DescribeSites) 用于查询一个或多个站点的详细信息。"
  },
  "DescribeSitesVerification": {
    "params": [
      {
        "name": "Urls",
        "desc": "站点的url列表"
      }
    ],
    "desc": "本接口 (DescribeSitesVerification) 用于查询一个或多个待验证站点的验证信息。"
  },
  "ModifySiteAttribute": {
    "params": [
      {
        "name": "SiteId",
        "desc": "站点ID"
      },
      {
        "name": "Name",
        "desc": "站点名称"
      }
    ],
    "desc": "本接口 (ModifySiteAttribute) 用于修改站点的属性。"
  },
  "ModifyConfigAttribute": {
    "params": [
      {
        "name": "NoticeLevel",
        "desc": "漏洞告警通知等级，4位分别代表：高危、中危、低危、提示"
      }
    ],
    "desc": "本接口 (ModifyConfigAttribute) 用于修改用户配置的属性。"
  },
  "DescribeMonitors": {
    "params": [
      {
        "name": "MonitorIds",
        "desc": "监控任务ID列表"
      },
      {
        "name": "Filters",
        "desc": "过滤条件"
      },
      {
        "name": "Offset",
        "desc": "偏移量，默认为0"
      },
      {
        "name": "Limit",
        "desc": "返回数量，默认为10，最大值为100"
      }
    ],
    "desc": "本接口 (DescribeMonitors) 用于查询一个或多个监控任务的详细信息。"
  },
  "DeleteMonitors": {
    "params": [
      {
        "name": "MonitorIds",
        "desc": "监控任务ID列表"
      }
    ],
    "desc": "本接口 (DeleteMonitors) 用于删除监控任务。"
  },
  "CreateMonitors": {
    "params": [
      {
        "name": "Urls",
        "desc": "站点的url列表"
      },
      {
        "name": "Name",
        "desc": "任务名称"
      },
      {
        "name": "ScannerType",
        "desc": "扫描模式，normal-正常扫描；deep-深度扫描"
      },
      {
        "name": "Crontab",
        "desc": "扫描周期，单位小时，每X小时执行一次"
      },
      {
        "name": "RateLimit",
        "desc": "扫描速率限制，每秒发送X个HTTP请求"
      },
      {
        "name": "FirstScanStartTime",
        "desc": "首次扫描开始时间"
      }
    ],
    "desc": "本接口（CreateMonitors）用于新增一个或多个站点的监测任务。"
  },
  "DeleteSites": {
    "params": [
      {
        "name": "SiteIds",
        "desc": "站点ID列表"
      }
    ],
    "desc": "本接口 (DeleteSites) 用于删除站点。"
  },
  "VerifySites": {
    "params": [
      {
        "name": "Urls",
        "desc": "站点的url列表"
      }
    ],
    "desc": "本接口 (VerifySites) 用于验证一个或多个待验证站点。"
  },
  "DescribeSiteQuota": {
    "params": [],
    "desc": "本接口 (DescribeSiteQuota) 用于查询用户购买的站点总数和已使用数。"
  }
}