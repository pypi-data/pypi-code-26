# -*- coding: utf-8 -*-
DESC = "vpc-2017-03-12"
INFO = {
  "ReplaceSecurityGroupPolicy": {
    "params": [
      {
        "name": "SecurityGroupId",
        "desc": "安全组实例ID，例如sg-33ocnj9n，可通过DescribeSecurityGroups获取。"
      },
      {
        "name": "SecurityGroupPolicySet",
        "desc": "安全组规则集合对象。"
      }
    ],
    "desc": "本接口（ReplaceSecurityGroupPolicy）用于替换单条安全组规则（SecurityGroupPolicy）。\n单个请求中只能替换单个方向的一条规则, 必须要指定索引（PolicyIndex）。"
  },
  "DeleteServiceTemplate": {
    "params": [
      {
        "name": "ServiceTemplateId",
        "desc": "协议端口模板实例ID，例如：ppm-e6dy460g。"
      }
    ],
    "desc": "删除协议端口模板"
  },
  "UnassignPrivateIpAddresses": {
    "params": [
      {
        "name": "NetworkInterfaceId",
        "desc": "弹性网卡实例ID，例如：eni-m6dyj72l。"
      },
      {
        "name": "PrivateIpAddresses",
        "desc": "指定的内网IP信息。"
      }
    ],
    "desc": "本接口（UnassignPrivateIpAddresses）用于弹性网卡退还内网 IP。\n* 退还弹性网卡上的辅助内网IP，接口自动解关联弹性公网 IP。不能退还弹性网卡的主内网IP。"
  },
  "DeleteAddressTemplateGroup": {
    "params": [
      {
        "name": "AddressTemplateGroupId",
        "desc": "IP地址模板集合实例ID，例如：ipmg-90cex8mq。"
      }
    ],
    "desc": "删除IP地址模板集合"
  },
  "DeleteServiceTemplateGroup": {
    "params": [
      {
        "name": "ServiceTemplateGroupId",
        "desc": "协议端口模板集合实例ID，例如：ppmg-n17uxvve。"
      }
    ],
    "desc": "删除协议端口模板集合"
  },
  "DescribeRouteTables": {
    "params": [
      {
        "name": "RouteTableIds",
        "desc": "路由表实例ID，例如：rtb-azd4dt1c。"
      },
      {
        "name": "Filters",
        "desc": "过滤条件，参数不支持同时指定RouteTableIds和Filters。\n<li>route-table-id - String - （过滤条件）路由表实例ID。</li>\n<li>route-table-name - String - （过滤条件）路由表名称。</li>\n<li>vpc-id - String - （过滤条件）VPC实例ID，形如：vpc-f49l6u0z。</li>\n<li>association.main - Boolean - （过滤条件）是否主路由表。</li>"
      },
      {
        "name": "Offset",
        "desc": "偏移量。"
      },
      {
        "name": "Limit",
        "desc": "请求对象个数。"
      }
    ],
    "desc": " 本接口（DescribeRouteTables）用于查询路由表。"
  },
  "CreateRouteTable": {
    "params": [
      {
        "name": "VpcId",
        "desc": "待操作的VPC实例ID。可通过DescribeVpcs接口返回值中的VpcId获取。"
      },
      {
        "name": "RouteTableName",
        "desc": "路由表名称，最大长度不能超过60个字节。"
      }
    ],
    "desc": "本接口(CreateRouteTable)用于创建路由表。\n* 创建了VPC后，系统会创建一个默认路由表，所有新建的子网都会关联到默认路由表。默认情况下您可以直接使用默认路由表来管理您的路由策略。当您的路由策略较多时，您可以调用创建路由表接口创建更多路由表管理您的路由策略。"
  },
  "ReplaceRouteTableAssociation": {
    "params": [
      {
        "name": "SubnetId",
        "desc": "子网实例ID，例如：subnet-3x5lf5q0。可通过DescribeSubnetEx接口查询。"
      },
      {
        "name": "RouteTableId",
        "desc": "路由表实例ID，例如：rtb-azd4dt1c。"
      }
    ],
    "desc": "本接口（ReplaceRouteTableAssociation)用于修改子网（Subnet）关联的路由表（RouteTable）。\n* 一个子网只能关联一个路由表。"
  },
  "AttachNetworkInterface": {
    "params": [
      {
        "name": "NetworkInterfaceId",
        "desc": "弹性网卡实例ID，例如：eni-m6dyj72l。"
      },
      {
        "name": "InstanceId",
        "desc": "CVM实例ID。形如：ins-r8hr2upy。"
      }
    ],
    "desc": "本接口（AttachNetworkInterface）用于弹性网卡绑定云主机。\n* 一个云主机可以绑定多个弹性网卡，但只能绑定一个主网卡。更多限制信息详见<a href=\"https://cloud.tencent.com/document/product/215/6513\">弹性网卡使用限制</a>。\n* 一个弹性网卡只能同时绑定一个云主机。\n* 只有运行中或者已关机状态的云主机才能绑定弹性网卡，查看云主机状态详见<a href=\"https://cloud.tencent.com/document/api/213/9452#instance_state\">腾讯云主机信息</a>。\n* 弹性网卡绑定的云主机必须是私有网络的，而且云主机所在可用区必须和弹性网卡子网的可用区相同。"
  },
  "ModifyServiceTemplateGroupAttribute": {
    "params": [
      {
        "name": "ServiceTemplateGroupId",
        "desc": "协议端口模板集合实例ID，例如：ppmg-ei8hfd9a。"
      },
      {
        "name": "ServiceTemplateGroupName",
        "desc": "协议端口模板集合名称。"
      },
      {
        "name": "ServiceTemplateIds",
        "desc": "协议端口模板实例ID，例如：ppm-4dw6agho。"
      }
    ],
    "desc": "本接口（ModifyServiceTemplateGroupAttribute）用于修改协议端口模板集合。"
  },
  "CreateVpc": {
    "params": [
      {
        "name": "VpcName",
        "desc": "vpc名称，最大长度不能超过60个字节。"
      },
      {
        "name": "CidrBlock",
        "desc": "vpc的cidr，只能为10.0.0.0/16，172.16.0.0/12，192.168.0.0/16这三个内网网段内。"
      },
      {
        "name": "EnableMulticast",
        "desc": "是否开启组播。true: 开启, false: 不开启。"
      },
      {
        "name": "DnsServers",
        "desc": "DNS地址，最多支持4个"
      },
      {
        "name": "DomainName",
        "desc": "域名"
      }
    ],
    "desc": "本接口(CreateVpc)用于创建私有网络(VPC)。\n* 用户可以创建的最小网段子网掩码为28（有16个IP地址），最大网段子网掩码为16（65,536个IP地址）,如果规划VPC网段请参见VPC网段规划说明。\n* 创建VPC时可同时把子网创建好，创建子网也请规划好子网网段及子网所在可用区，同一个VPC内子网网段不能重叠，不同可用区可以做跨可用区容灾，详见VPC可用区说明。\n* 如果您同时创建了子网，系统会创建一个默认路由表，系统会把子网关联到这个默认路由表。\n* 同一个地域能创建的VPC资源个数也是有限制的，详见 <a href=\"https://cloud.tencent.com/doc/product/215/537\" title=\"VPC使用限制\">VPC使用限制</a>,如果需要扩充请联系在线客服。"
  },
  "DeleteSecurityGroupPolicies": {
    "params": [
      {
        "name": "SecurityGroupId",
        "desc": "安全组实例ID，例如sg-33ocnj9n，可通过DescribeSecurityGroups获取。"
      },
      {
        "name": "SecurityGroupPolicySet",
        "desc": "安全组规则集合。一个请求中只能删除单个方向的一条或多条规则。支持指定索引（PolicyIndex） 匹配删除和安全组规则匹配删除两种方式，一个请求中只能使用一种匹配方式。"
      }
    ],
    "desc": "本接口（DeleteSecurityGroupPolicies）用于用于删除安全组规则（SecurityGroupPolicy）。\n* SecurityGroupPolicySet.Version 用于指定要操作的安全组的版本。传入 Version 版本号若不等于当前安全组的最新版本，将返回失败；若不传 Version 则直接删除指定PolicyIndex的规则。"
  },
  "DescribeAddressQuota": {
    "params": [],
    "desc": "本接口 (DescribeAddressQuota) 用于查询您账户的[弹性公网IP](https://cloud.tencent.com/document/product/213/1941)（简称 EIP）在当前地域的配额信息。配额详情可参见 [EIP 产品简介](https://cloud.tencent.com/document/product/213/5733)。"
  },
  "ResetRoutes": {
    "params": [
      {
        "name": "RouteTableId",
        "desc": "路由表实例ID，例如：rtb-azd4dt1c。"
      },
      {
        "name": "RouteTableName",
        "desc": "路由表名称，最大长度不能超过60个字节。"
      },
      {
        "name": "Routes",
        "desc": "路由策略。"
      }
    ],
    "desc": "本接口（ResetRoutes）用于对某个路由表名称和所有路由策略（Route）进行重新设置。\n注意: 调用本接口是先删除当前路由表中所有路由策略, 再保存新提交的路由策略内容, 会引起网络中断。"
  },
  "DeleteVpc": {
    "params": [
      {
        "name": "VpcId",
        "desc": "VPC实例ID。可通过DescribeVpcs接口返回值中的VpcId获取。"
      }
    ],
    "desc": "本接口（DeleteVpc）用于删除私有网络。\n* 删除前请确保 VPC 内已经没有相关资源，例如云主机、云数据库、NoSQL、VPN网关、专线网关、负载均衡、对等连接、与之互通的基础网络设备等。\n* 删除私有网络是不可逆的操作，请谨慎处理。"
  },
  "DeleteAddressTemplate": {
    "params": [
      {
        "name": "AddressTemplateId",
        "desc": "IP地址模板实例ID，例如：ipm-09o5m8kc。"
      }
    ],
    "desc": "删除IP地址模板"
  },
  "DeleteNetworkInterface": {
    "params": [
      {
        "name": "NetworkInterfaceId",
        "desc": "弹性网卡实例ID，例如：eni-m6dyj72l。"
      }
    ],
    "desc": "本接口（DeleteNetworkInterface）用于创建弹性网卡。\n* 弹性网卡上绑定了云主机时，不能被删除。\n* 删除指定弹性网卡，弹性网卡必须先和子机解绑才能删除。删除之后弹性网卡上所有内网IP都将被退还。"
  },
  "AllocateAddresses": {
    "params": [
      {
        "name": "AddressCount",
        "desc": "申请 EIP 数量，默认值为1。"
      }
    ],
    "desc": "本接口 (AllocateAddresses) 用于申请一个或多个[弹性公网IP](https://cloud.tencent.com/document/product/213/1941)（简称 EIP）。\n* EIP 是专为动态云计算设计的静态 IP 地址。借助 EIP，您可以快速将 EIP 重新映射到您的另一个实例上，从而屏蔽实例故障。\n* 您的 EIP 与腾讯云账户相关联，而不是与某个实例相关联。在您选择显式释放该地址，或欠费超过七天之前，它会一直与您的腾讯云账户保持关联。\n* 平台对用户每地域能申请的 EIP 最大配额有所限制，可参见 [EIP 产品简介](https://cloud.tencent.com/document/product/213/5733)，上述配额可通过 DescribeAddressQuota 接口获取。"
  },
  "ModifyAddressTemplateAttribute": {
    "params": [
      {
        "name": "AddressTemplateId",
        "desc": "IP地址模板实例ID，例如：ipm-mdunqeb6。"
      },
      {
        "name": "AddressTemplateName",
        "desc": "IP地址模板名称。"
      },
      {
        "name": "Addresses",
        "desc": "地址信息，支持 IP、CIDR、IP 范围。"
      }
    ],
    "desc": "修改IP地址模板"
  },
  "DescribeSecurityGroupPolicies": {
    "params": [
      {
        "name": "SecurityGroupId",
        "desc": "安全组实例ID，例如：sg-33ocnj9n，可通过DescribeSecurityGroups获取。"
      }
    ],
    "desc": "本接口（DescribeSecurityGroupPolicies）用于查询安全组规则。"
  },
  "DescribeSecurityGroups": {
    "params": [
      {
        "name": "SecurityGroupIds",
        "desc": "安全组实例ID，例如：sg-33ocnj9n，可通过DescribeSecurityGroups获取。每次请求的实例的上限为100。参数不支持同时指定SecurityGroupIds和Filters。"
      },
      {
        "name": "Filters",
        "desc": "过滤条件，参数不支持同时指定SecurityGroupIds和Filters。\n<li>project-id - Integer - （过滤条件）项目id。</li>\n<li>security-group-name - String - （过滤条件）安全组名称。</li>"
      },
      {
        "name": "Offset",
        "desc": "偏移量。"
      },
      {
        "name": "Limit",
        "desc": "返回数量。"
      }
    ],
    "desc": "本接口（DescribeSecurityGroups）用于查询安全组。"
  },
  "MigrateNetworkInterface": {
    "params": [
      {
        "name": "NetworkInterfaceId",
        "desc": "弹性网卡实例ID，例如：eni-m6dyj72l。"
      },
      {
        "name": "SourceInstanceId",
        "desc": "弹性网卡当前绑定的CVM实例ID。形如：ins-r8hr2upy。"
      },
      {
        "name": "DestinationInstanceId",
        "desc": "待迁移的目的CVM实例ID。"
      }
    ],
    "desc": "本接口（MigrateNetworkInterface）用于弹性网卡迁移。"
  },
  "AssignPrivateIpAddresses": {
    "params": [
      {
        "name": "NetworkInterfaceId",
        "desc": "弹性网卡实例ID，例如：eni-m6dyj72l。"
      },
      {
        "name": "PrivateIpAddresses",
        "desc": "指定的内网IP信息。"
      },
      {
        "name": "SecondaryPrivateIpAddressCount",
        "desc": "新申请的内网IP地址个数。"
      }
    ],
    "desc": "本接口（AssignPrivateIpAddresses）用于弹性网卡申请内网 IP。\n* 一个弹性网卡支持绑定的IP地址是有限制的，更多资源限制信息详见<a href=\"https://cloud.tencent.com/document/product/215/6513\">弹性网卡使用限制</a>。\n* 可以指定内网IP地址申请，内网IP地址类型不能为主IP，主IP已存在，不能修改，内网IP必须要弹性网卡所在子网内，而且不能被占用。\n* 在弹性网卡上申请一个到多个辅助内网IP，接口会在弹性网卡所在子网网段内返回指定数量的辅助内网IP。"
  },
  "ModifyPrivateIpAddressesAttribute": {
    "params": [
      {
        "name": "NetworkInterfaceId",
        "desc": "弹性网卡实例ID，例如：eni-m6dyj72l。"
      },
      {
        "name": "PrivateIpAddresses",
        "desc": "指定的内网IP信息。"
      }
    ],
    "desc": "本接口（ModifyPrivateIpAddressesAttribute）用于修改弹性网卡内网IP属性。"
  },
  "CreateServiceTemplate": {
    "params": [
      {
        "name": "ServiceTemplateName",
        "desc": "协议端口模板名称"
      },
      {
        "name": "Services",
        "desc": "支持单个端口、多个端口、连续端口及所有端口，协议支持：TCP、UDP、ICMP、GRE 协议。"
      }
    ],
    "desc": "创建协议端口模板"
  },
  "DescribeAddresses": {
    "params": [
      {
        "name": "AddressIds",
        "desc": "标识 EIP 的唯一 ID 列表。EIP 唯一 ID 形如：`eip-11112222`。参数不支持同时指定`AddressIds`和`Filters`。"
      },
      {
        "name": "Filters",
        "desc": "每次请求的`Filters`的上限为10，`Filter.Values`的上限为5。参数不支持同时指定`AddressIds`和`Filters`。详细的过滤条件如下：\n<li> address-id - String - 是否必填：否 - （过滤条件）按照 EIP 的唯一 ID 过滤。EIP 唯一 ID 形如：eip-11112222。</li>\n<li> address-name - String - 是否必填：否 - （过滤条件）按照 EIP 名称过滤。不支持模糊过滤。</li>\n<li> address-ip - String - 是否必填：否 - （过滤条件）按照 EIP 的 IP 地址过滤。</li>\n<li> address-status - String - 是否必填：否 - （过滤条件）按照 EIP 的状态过滤。取值范围：[详见EIP状态列表](https://cloud.tencent.com/document/api/213/9452#eip_state)。</li>\n<li> instance-id - String - 是否必填：否 - （过滤条件）按照 EIP 绑定的实例 ID 过滤。实例 ID 形如：ins-11112222。</li>\n<li> private-ip-address - String - 是否必填：否 - （过滤条件）按照 EIP 绑定的内网 IP 过滤。</li>\n<li> network-interface-id - String - 是否必填：否 - （过滤条件）按照 EIP 绑定的弹性网卡 ID 过滤。弹性网卡 ID 形如：eni-11112222。</li>\n<li> is-arrears - String - 是否必填：否 - （过滤条件）按照 EIP 是否欠费进行过滤。（TRUE：EIP 处于欠费状态|FALSE：EIP 费用状态正常）</li>"
      },
      {
        "name": "Offset",
        "desc": "偏移量，默认为0。关于`Offset`的更进一步介绍请参考 API [简介](https://cloud.tencent.com/document/api/213/11646)中的相关小节。"
      },
      {
        "name": "Limit",
        "desc": "返回数量，默认为20，最大值为100。关于`Limit`的更进一步介绍请参考 API [简介](https://cloud.tencent.com/document/api/213/11646)中的相关小节。"
      }
    ],
    "desc": "本接口 (DescribeAddresses) 用于查询一个或多个[弹性公网IP](https://cloud.tencent.com/document/product/213/1941)（简称 EIP）的详细信息。\n* 如果参数为空，返回当前用户一定数量（Limit所指定的数量，默认为20）的 EIP。"
  },
  "AssociateAddress": {
    "params": [
      {
        "name": "AddressId",
        "desc": "标识 EIP 的唯一 ID。EIP 唯一 ID 形如：`eip-11112222`。"
      },
      {
        "name": "InstanceId",
        "desc": "要绑定的实例 ID。实例 ID 形如：`ins-11112222`。可通过登录[控制台](https://console.cloud.tencent.com/cvm)查询，也可通过 [DescribeInstances](https://cloud.tencent.com/document/api/213/9389) 接口返回值中的`InstanceId`获取。"
      },
      {
        "name": "NetworkInterfaceId",
        "desc": "要绑定的弹性网卡 ID。 弹性网卡 ID 形如：`eni-11112222`。`NetworkInterfaceId` 与 `InstanceId` 不可同时指定。弹性网卡 ID 可通过登录[控制台](https://console.cloud.tencent.com/vpc/eni)查询，也可通过[DescribeNetworkInterfaces](https://cloud.tencent.com/document/api/215/4814)接口返回值中的`networkInterfaceId`获取。"
      },
      {
        "name": "PrivateIpAddress",
        "desc": "要绑定的内网 IP。如果指定了 `NetworkInterfaceId` 则也必须指定 `PrivateIpAddress` ，表示将 EIP 绑定到指定弹性网卡的指定内网 IP 上。同时要确保指定的 `PrivateIpAddress` 是指定的 `NetworkInterfaceId` 上的一个内网 IP。指定弹性网卡的内网 IP 可通过登录[控制台](https://console.cloud.tencent.com/vpc/eni)查询，也可通过[DescribeNetworkInterfaces](https://cloud.tencent.com/document/api/215/4814)接口返回值中的`privateIpAddress`获取。"
      }
    ],
    "desc": "本接口 (AssociateAddress) 用于将[弹性公网IP](https://cloud.tencent.com/document/product/213/1941)（简称 EIP）绑定到实例或弹性网卡的指定内网 IP 上。\n* 将 EIP 绑定到实例上，其本质是将 EIP 绑定到实例上主网卡的主内网 IP 上。\n* 将 EIP 绑定到主网卡的主内网IP上，绑定过程会把其上绑定的普通公网 IP 自动解绑并释放。\n* 如果指定网卡的内网 IP 已经绑定了 EIP，则必须先解绑该 EIP，才能再绑定新的。\n* EIP 如果欠费或被封堵，则不能被绑定。\n* 只有状态为 UNBIND 的 EIP 才能够被绑定。"
  },
  "DeleteRoutes": {
    "params": [
      {
        "name": "RouteTableId",
        "desc": "路由表实例ID。"
      },
      {
        "name": "Routes",
        "desc": "路由策略对象。"
      }
    ],
    "desc": "本接口(DeleteRoutes)用于对某个路由表批量删除路由策略（Route）。"
  },
  "ModifySecurityGroupPolicies": {
    "params": [
      {
        "name": "SecurityGroupId",
        "desc": "安全组实例ID，例如sg-33ocnj9n，可通过DescribeSecurityGroups获取。"
      },
      {
        "name": "SecurityGroupPolicySet",
        "desc": "安全组规则集合。 SecurityGroupPolicySet对象必须同时指定新的出（Egress）入（Ingress）站规则。 SecurityGroupPolicy对象不支持自定义索引（PolicyIndex）。"
      }
    ],
    "desc": "本接口（ModifySecurityGroupPolicies）用于重置安全组出站和入站规则（SecurityGroupPolicy）。\n\n* 接口是先删除当前所有的出入站规则，然后再添加 Egress 和 Ingress 规则，不支持自定义索引 PolicyIndex 。\n* 如果指定 SecurityGroupPolicySet.Version 为0, 表示清空所有规则，并忽略Egress和Ingress。\n* Protocol字段支持输入TCP, UDP, ICMP, GRE, ALL。\n* CidrBlock字段允许输入符合cidr格式标准的任意字符串。(展开)在基础网络中，如果CidrBlock包含您的账户内的云服务器之外的设备在腾讯云的内网IP，并不代表此规则允许您访问这些设备，租户之间网络隔离规则优先于安全组中的内网规则。\n* SecurityGroupId字段允许输入与待修改的安全组位于相同项目中的安全组ID，包括这个安全组ID本身，代表安全组下所有云服务器的内网IP。使用这个字段时，这条规则用来匹配网络报文的过程中会随着被使用的这个ID所关联的云服务器变化而变化，不需要重新修改。\n* Port字段允许输入一个单独端口号，或者用减号分隔的两个端口号代表端口范围，例如80或8000-8010。只有当Protocol字段是TCP或UDP时，Port字段才被接受。\n* Action字段只允许输入ACCEPT或DROP。\n* CidrBlock, SecurityGroupId, AddressTemplate三者是排他关系，不允许同时输入，Protocol + Port和ServiceTemplate二者是排他关系，不允许同时输入。"
  },
  "DetachClassicLinkVpc": {
    "params": [
      {
        "name": "VpcId",
        "desc": "VPC实例ID。可通过DescribeVpcs接口返回值中的VpcId获取。"
      },
      {
        "name": "InstanceIds",
        "desc": "CVM实例ID查询。形如：ins-r8hr2upy。"
      }
    ],
    "desc": "本接口(DetachClassicLinkVpc)用于删除私有网络和基础网络设备互通。"
  },
  "DeleteSubnet": {
    "params": [
      {
        "name": "SubnetId",
        "desc": "子网实例ID。可通过DescribeSubnets接口返回值中的SubnetId获取。"
      }
    ],
    "desc": "本接口（DeleteSubnet）用于用于删除子网(Subnet)。\n* 删除子网前，请清理该子网下所有资源，包括云主机、负载均衡、云数据、noSql、弹性网卡等资源。"
  },
  "ModifySecurityGroupAttribute": {
    "params": [
      {
        "name": "SecurityGroupId",
        "desc": "安全组实例ID，例如sg-33ocnj9n，可通过DescribeSecurityGroups获取。"
      },
      {
        "name": "GroupName",
        "desc": "安全组名称，可任意命名，但不得超过60个字符。"
      },
      {
        "name": "GroupDescription",
        "desc": "安全组备注，最多100个字符。"
      }
    ],
    "desc": "本接口（ModifySecurityGroupAttribute）用于修改安全组（SecurityGroupPolicy）属性。"
  },
  "AttachClassicLinkVpc": {
    "params": [
      {
        "name": "VpcId",
        "desc": "VPC实例ID"
      },
      {
        "name": "InstanceIds",
        "desc": "CVM实例ID"
      }
    ],
    "desc": "本接口(AttachClassicLinkVpc)用于私有网络和基础网络设备互通。\n* 私有网络和基础网络设备必须在同一个地域。\n* 私有网络和基础网络的区别详见vpc产品文档-<a href=\"https://cloud.tencent.com/document/product/215/535#2.-.E7.A7.81.E6.9C.89.E7.BD.91.E7.BB.9C.E4.B8.8E.E5.9F.BA.E7.A1.80.E7.BD.91.E7.BB.9C\">私有网络与基础网络</a>。"
  },
  "DeleteSecurityGroup": {
    "params": [
      {
        "name": "SecurityGroupId",
        "desc": "安全组实例ID，例如sg-33ocnj9n，可通过DescribeSecurityGroups获取。"
      }
    ],
    "desc": "本接口（DeleteSecurityGroup）用于删除安全组（SecurityGroup）。\n* 只有当前账号下的安全组允许被删除。\n* 安全组实例ID如果在其他安全组的规则中被引用，则无法直接删除。这种情况下，需要先进行规则修改，再删除安全组。\n* 删除的安全组无法再找回，请谨慎调用。"
  },
  "DescribeSubnets": {
    "params": [
      {
        "name": "SubnetIds",
        "desc": "子网实例ID查询。形如：subnet-pxir56ns。每次请求的实例的上限为100。参数不支持同时指定SubnetIds和Filters。"
      },
      {
        "name": "Filters",
        "desc": "过滤条件，参数不支持同时指定SubnetIds和Filters。\n<li>subnet-id - String - （过滤条件）Subnet实例名称。</li>\n<li>vpc-id - String - （过滤条件）VPC实例ID，形如：vpc-f49l6u0z。</li>\n<li>cidr-block - String - （过滤条件）vpc的cidr。</li>\n<li>is-default - Boolean - （过滤条件）是否是默认子网。</li>\n<li>subnet-name - String - （过滤条件）子网名称。</li>\n<li>zone - String - （过滤条件）可用区。</li>"
      },
      {
        "name": "Offset",
        "desc": "偏移量"
      },
      {
        "name": "Limit",
        "desc": "返回数量"
      }
    ],
    "desc": "本接口（DescribeSubnets）用于查询子网列表。"
  },
  "DescribeServiceTemplateGroups": {
    "params": [
      {
        "name": "Filters",
        "desc": "过滤条件。\n<li>service-template-group-name - String - （过滤条件）协议端口模板集合名称。</li>\n<li>service-template-group-id - String - （过滤条件）协议端口模板集合实例ID，例如：ppmg-e6dy460g。</li>"
      },
      {
        "name": "Offset",
        "desc": "偏移量，默认为0。"
      },
      {
        "name": "Limit",
        "desc": "返回数量，默认为20，最大值为100。"
      }
    ],
    "desc": "查询协议端口模板集合"
  },
  "ModifyServiceTemplateAttribute": {
    "params": [
      {
        "name": "ServiceTemplateId",
        "desc": "协议端口模板实例ID，例如：ppm-529nwwj8。"
      },
      {
        "name": "ServiceTemplateName",
        "desc": "协议端口模板名称。"
      },
      {
        "name": "Services",
        "desc": "支持单个端口、多个端口、连续端口及所有端口，协议支持：TCP、UDP、ICMP、GRE 协议。"
      }
    ],
    "desc": "修改协议端口模板"
  },
  "ModifyRouteTableAttribute": {
    "params": [
      {
        "name": "RouteTableId",
        "desc": "路由表实例ID，例如：rtb-azd4dt1c。"
      },
      {
        "name": "RouteTableName",
        "desc": "路由表名称。"
      }
    ],
    "desc": "本接口（ModifyRouteTableAttribute）用于修改路由表（RouteTable）属性。"
  },
  "DescribeClassicLinkInstances": {
    "params": [
      {
        "name": "Filters",
        "desc": "过滤条件。\n<li>vpc-id - String - （过滤条件）VPC实例ID。</li>\n<li>vm-ip - String - （过滤条件）基础网络云主机IP。</li>"
      },
      {
        "name": "Offset",
        "desc": "偏移量"
      },
      {
        "name": "Limit",
        "desc": "返回数量"
      }
    ],
    "desc": "本接口(DescribeClassicLinkInstances)用于私有网络和基础网络设备互通。"
  },
  "CreateNetworkInterface": {
    "params": [
      {
        "name": "VpcId",
        "desc": "VPC实例ID。可通过DescribeVpcs接口返回值中的VpcId获取。"
      },
      {
        "name": "NetworkInterfaceName",
        "desc": "弹性网卡名称，最大长度不能超过60个字节。"
      },
      {
        "name": "NetworkInterfaceDescription",
        "desc": "弹性网卡描述，可任意命名，但不得超过60个字符。"
      },
      {
        "name": "SubnetId",
        "desc": "弹性网卡所在的子网实例ID，例如：subnet-0ap8nwca。"
      },
      {
        "name": "SecondaryPrivateIpAddressCount",
        "desc": "新申请的内网IP地址个数。"
      },
      {
        "name": "SecurityGroupIds",
        "desc": "指定绑定的安全组，例如：['sg-1dd51d']。"
      },
      {
        "name": "PrivateIpAddresses",
        "desc": "指定内网IP信息。"
      }
    ],
    "desc": "本接口（CreateNetworkInterface）用于创建弹性网卡。\n* 创建弹性网卡时可以指定内网IP，并且可以指定一个主IP，指定的内网IP必须在弹性网卡所在子网内，而且不能被占用。\n* 创建弹性网卡时可以指定需要申请的内网IP数量，系统会随机生成内网IP地址。\n* 创建弹性网卡同时可以绑定已有安全组。"
  },
  "ModifyAddressTemplateGroupAttribute": {
    "params": [
      {
        "name": "AddressTemplateGroupId",
        "desc": "IP地址模板集合实例ID，例如：ipmg-2uw6ujo6。"
      },
      {
        "name": "AddressTemplateGroupName",
        "desc": "IP地址模板集合名称。"
      },
      {
        "name": "AddressTemplateIds",
        "desc": "IP地址模板实例ID， 例如：ipm-mdunqeb6。"
      }
    ],
    "desc": "修改IP地址模板集合"
  },
  "CreateAddressTemplateGroup": {
    "params": [
      {
        "name": "AddressTemplateGroupName",
        "desc": "IP地址模版集合名称。"
      },
      {
        "name": "AddressTemplateIds",
        "desc": "IP地址模版实例ID，例如：ipm-mdunqeb6。"
      }
    ],
    "desc": "创建IP地址模版集合"
  },
  "CreateSecurityGroup": {
    "params": [
      {
        "name": "ProjectId",
        "desc": "项目id，默认0。可在qcloud控制台项目管理页面查询到。"
      },
      {
        "name": "GroupName",
        "desc": "安全组名称，可任意命名，但不得超过60个字符。"
      },
      {
        "name": "GroupDescription",
        "desc": "安全组备注，最多100个字符。"
      }
    ],
    "desc": "本接口（CreateSecurityGroup）用于创建新的安全组（SecurityGroup）。\n* 每个账户下每个地域的每个项目的<a href=\"https://cloud.tencent.com/document/product/213/500#2.-.E5.AE.89.E5.85.A8.E7.BB.84.E7.9A.84.E9.99.90.E5.88.B6\">安全组数量限制</a>。\n* 新建的安全组的入站和出站规则默认都是全部拒绝，在创建后通常您需要再调用CreateSecurityGroupPolicies将安全组的规则设置为需要的规则。"
  },
  "CreateRoutes": {
    "params": [
      {
        "name": "RouteTableId",
        "desc": "路由表实例ID。"
      },
      {
        "name": "Routes",
        "desc": "路由策略对象。"
      }
    ],
    "desc": "本接口(CreateRoutes)用于创建路由策略。\n* 向指定路由表批量新增路由策略。"
  },
  "DescribeServiceTemplates": {
    "params": [
      {
        "name": "Filters",
        "desc": "过滤条件。\n<li>service-template-name - String - （过滤条件）协议端口模板名称。</li>\n<li>service-template-id - String - （过滤条件）协议端口模板实例ID，例如：ppm-e6dy460g。</li>"
      },
      {
        "name": "Offset",
        "desc": "偏移量，默认为0。"
      },
      {
        "name": "Limit",
        "desc": "返回数量，默认为20，最大值为100。"
      }
    ],
    "desc": "查询协议端口模板"
  },
  "ModifyNetworkInterfaceAttribute": {
    "params": [
      {
        "name": "NetworkInterfaceId",
        "desc": "弹性网卡实例ID，例如：eni-pxir56ns。"
      },
      {
        "name": "NetworkInterfaceName",
        "desc": "弹性网卡名称，最大长度不能超过60个字节。"
      },
      {
        "name": "NetworkInterfaceDescription",
        "desc": "弹性网卡描述，可任意命名，但不得超过60个字符。"
      },
      {
        "name": "SecurityGroupIds",
        "desc": "指定绑定的安全组，例如:['sg-1dd51d']。"
      }
    ],
    "desc": "本接口（ModifyNetworkInterfaceAttribute）用于修改弹性网卡属性。"
  },
  "ReleaseAddresses": {
    "params": [
      {
        "name": "AddressIds",
        "desc": "标识 EIP 的唯一 ID 列表。EIP 唯一 ID 形如：`eip-11112222`。"
      }
    ],
    "desc": "本接口 (ReleaseAddresses) 用于释放一个或多个[弹性公网IP](https://cloud.tencent.com/document/product/213/1941)（简称 EIP）。\n* 该操作不可逆，释放后 EIP 关联的 IP 地址将不再属于您的名下。\n* 只有状态为 UNBIND 的 EIP 才能进行释放操作。"
  },
  "DetachNetworkInterface": {
    "params": [
      {
        "name": "NetworkInterfaceId",
        "desc": "弹性网卡实例ID，例如：eni-m6dyj72l。"
      },
      {
        "name": "InstanceId",
        "desc": "CVM实例ID。形如：ins-r8hr2upy。"
      }
    ],
    "desc": "本接口（DetachNetworkInterface）用于弹性网卡解绑云主机。"
  },
  "ModifySubnetAttribute": {
    "params": [
      {
        "name": "SubnetId",
        "desc": "子网实例ID。形如：subnet-pxir56ns。"
      },
      {
        "name": "SubnetName",
        "desc": "子网名称，最大长度不能超过60个字节。"
      },
      {
        "name": "EnableBroadcast",
        "desc": "子网是否开启广播。"
      }
    ],
    "desc": "本接口（ModifySubnetAttribute）用于修改子网属性。"
  },
  "CreateServiceTemplateGroup": {
    "params": [
      {
        "name": "ServiceTemplateGroupName",
        "desc": "协议端口模板集合名称"
      },
      {
        "name": "ServiceTemplateIds",
        "desc": "协议端口模板实例ID，例如：ppm-4dw6agho。"
      }
    ],
    "desc": "创建协议端口模板集合"
  },
  "ModifyVpcAttribute": {
    "params": [
      {
        "name": "VpcId",
        "desc": "VPC实例ID。形如：vpc-f49l6u0z。每次请求的实例的上限为100。参数不支持同时指定VpcIds和Filters。"
      },
      {
        "name": "VpcName",
        "desc": "私有网络名称，可任意命名，但不得超过60个字符。"
      },
      {
        "name": "EnableMulticast",
        "desc": "是否开启组播。true: 开启, false: 关闭。"
      },
      {
        "name": "DnsServers",
        "desc": "DNS地址，最多支持4个，第1个默认为主，其余为备"
      },
      {
        "name": "DomainName",
        "desc": "域名"
      }
    ],
    "desc": "本接口（ModifyVpcAttribute）用于修改私有网络（VPC）的相关属性。"
  },
  "DeleteRouteTable": {
    "params": [
      {
        "name": "RouteTableId",
        "desc": "路由表实例ID，例如：rtb-azd4dt1c。"
      }
    ],
    "desc": "删除路由表"
  },
  "DisassociateAddress": {
    "params": [
      {
        "name": "AddressId",
        "desc": "标识 EIP 的唯一 ID。EIP 唯一 ID 形如：`eip-11112222`。"
      },
      {
        "name": "ReallocateNormalPublicIp",
        "desc": "表示解绑 EIP 之后是否分配普通公网 IP。取值范围：<br><li>TRUE：表示解绑 EIP 之后分配普通公网 IP。<br><li>FALSE：表示解绑 EIP 之后不分配普通公网 IP。<br>默认取值：FALSE。<br><br>只有满足以下条件时才能指定该参数：<br><li> 只有在解绑主网卡的主内网 IP 上的 EIP 时才能指定该参数。<br><li>解绑 EIP 后重新分配普通公网 IP 操作一个账号每天最多操作 10 次；详情可通过 [DescribeAddressQuota](https://cloud.tencent.com/document/api/213/1378) 接口获取。"
      }
    ],
    "desc": "本接口 (DisassociateAddress) 用于解绑[弹性公网IP](https://cloud.tencent.com/document/product/213/1941)（简称 EIP）。\n* 只有状态为 BIND 和 BIND_ENI 的 EIP 才能进行解绑定操作。\n* EIP 如果被封堵，则不能进行解绑定操作。"
  },
  "DescribeAddressTemplates": {
    "params": [
      {
        "name": "Filters",
        "desc": "过滤条件。\n<li>address-template-name - String - （过滤条件）IP地址模板名称。</li>\n<li>address-template-id - String - （过滤条件）IP地址模板实例ID，例如：ipm-mdunqeb6。</li>"
      },
      {
        "name": "Offset",
        "desc": "偏移量，默认为0。"
      },
      {
        "name": "Limit",
        "desc": "返回数量，默认为20，最大值为100。"
      }
    ],
    "desc": "查询IP地址模板"
  },
  "CreateAddressTemplate": {
    "params": [
      {
        "name": "AddressTemplateName",
        "desc": "IP地址模版名称"
      },
      {
        "name": "Addresses",
        "desc": "地址信息，支持 IP、CIDR、IP 范围。"
      }
    ],
    "desc": "创建IP地址模版"
  },
  "ModifyAddressAttribute": {
    "params": [
      {
        "name": "AddressId",
        "desc": "标识 EIP 的唯一 ID。EIP 唯一 ID 形如：`eip-11112222`。"
      },
      {
        "name": "AddressName",
        "desc": "修改后的 EIP 名称。长度上限为20个字符。"
      }
    ],
    "desc": "本接口 (ModifyAddressAttribute) 用于修改[弹性公网IP](https://cloud.tencent.com/document/product/213/1941)（简称 EIP）的名称。"
  },
  "DescribeAddressTemplateGroups": {
    "params": [
      {
        "name": "Filters",
        "desc": "过滤条件。\n<li>address-template-group-name - String - （过滤条件）IP地址模板集合名称。</li>\n<li>address-template-group-id - String - （过滤条件）IP地址模板实集合例ID，例如：ipmg-mdunqeb6。</li>"
      },
      {
        "name": "Offset",
        "desc": "偏移量，默认为0。"
      },
      {
        "name": "Limit",
        "desc": "返回数量，默认为20，最大值为100。"
      }
    ],
    "desc": "查询IP地址模板集合"
  },
  "DescribeVpcs": {
    "params": [
      {
        "name": "VpcIds",
        "desc": "VPC实例ID。形如：vpc-f49l6u0z。每次请求的实例的上限为100。参数不支持同时指定VpcIds和Filters。"
      },
      {
        "name": "Filters",
        "desc": "过滤条件，参数不支持同时指定VpcIds和Filters。\n<li>vpc-name - String - （过滤条件）VPC实例名称。</li>\n<li>is-default - Boolean - （过滤条件）是否默认VPC。</li>\n<li>vpc-id - String - （过滤条件）VPC实例ID形如：vpc-f49l6u0z。</li>\n<li>cidr-block - String - （过滤条件）vpc的cidr。</li>"
      },
      {
        "name": "Offset",
        "desc": "偏移量"
      },
      {
        "name": "Limit",
        "desc": "返回数量"
      }
    ],
    "desc": "本接口（DescribeVpcs）用于查询私有网络列表。"
  },
  "TransformAddress": {
    "params": [
      {
        "name": "InstanceId",
        "desc": "待操作有普通公网 IP 的实例 ID。实例 ID 形如：`ins-11112222`。可通过登录[控制台](https://console.cloud.tencent.com/cvm)查询，也可通过 [DescribeInstances](https://cloud.tencent.com/document/api/213/9389) 接口返回值中的`InstanceId`获取。"
      }
    ],
    "desc": "本接口 (TransformAddress) 用于将实例的普通公网 IP 转换为[弹性公网IP](https://cloud.tencent.com/document/product/213/1941)（简称 EIP）。\n* 平台对用户每地域每日解绑 EIP 重新分配普通公网 IP 次数有所限制（可参见 [EIP 产品简介](/document/product/213/1941)）。上述配额可通过 [DescribeAddressQuota](https://cloud.tencent.com/document/api/213/1378) 接口获取。"
  },
  "DescribeNetworkInterfaces": {
    "params": [
      {
        "name": "NetworkInterfaceIds",
        "desc": "弹性网卡实例ID查询。形如：eni-pxir56ns。每次请求的实例的上限为100。参数不支持同时指定NetworkInterfaceIds和Filters。"
      },
      {
        "name": "Filters",
        "desc": "过滤条件，参数不支持同时指定NetworkInterfaceIds和Filters。\n<li>vpc-id - String - （过滤条件）VPC实例ID，形如：vpc-f49l6u0z。</li>\n<li>subnet-id - String - （过滤条件）所属子网实例ID，形如：subnet-f49l6u0z。</li>\n<li>network-interface-id - String - （过滤条件）弹性网卡实例ID，形如：eni-5k56k7k7。</li>\n<li>attachment.instance-id - String - （过滤条件）绑定的云服务器实例ID，形如：ins-3nqpdn3i。</li>\n<li>groups.security-group-id - String - （过滤条件）绑定的安全组实例ID，例如：sg-f9ekbxeq。</li>\n<li>network-interface-name - String - （过滤条件）网卡实例名称。</li>\n<li>network-interface-description - String - （过滤条件）网卡实例描述。</li>"
      },
      {
        "name": "Offset",
        "desc": "偏移量，默认为0。"
      },
      {
        "name": "Limit",
        "desc": "返回数量，默认为20，最大值为100。"
      }
    ],
    "desc": "本接口（DescribeNetworkInterfaces）用于查询弹性网卡列表。"
  },
  "MigratePrivateIpAddress": {
    "params": [
      {
        "name": "SourceNetworkInterfaceId",
        "desc": "当内网IP绑定的弹性网卡实例ID，例如：eni-m6dyj72l。"
      },
      {
        "name": "DestinationNetworkInterfaceId",
        "desc": "待迁移的目的弹性网卡实例ID。"
      },
      {
        "name": "PrivateIpAddress",
        "desc": "迁移的内网IP地址，例如：10.0.0.6。"
      }
    ],
    "desc": " 本接口（MigratePrivateIpAddress）用于弹性网卡内网IP迁移。\n\n* 该接口用于将一个内网IP从一个弹性网卡上迁移到另外一个弹性网卡，主IP地址不支持迁移。\n* 迁移前后的弹性网卡必须在同一个子网内。"
  },
  "CreateSecurityGroupPolicies": {
    "params": [
      {
        "name": "SecurityGroupId",
        "desc": "安全组实例ID，例如sg-33ocnj9n，可通过DescribeSecurityGroups获取。"
      },
      {
        "name": "SecurityGroupPolicySet",
        "desc": "安全组规则集合。"
      }
    ],
    "desc": "本接口（CreateSecurityGroupPolicies）用于创建安全组规则（SecurityGroupPolicy）。\n\n* Version安全组规则版本号，用户每次更新安全规则版本会自动加1，防止你更新的路由规则已过期，不填不考虑冲突。\n* Protocol字段支持输入TCP, UDP, ICMP, GRE, ALL。\n* CidrBlock字段允许输入符合cidr格式标准的任意字符串。(展开)在基础网络中，如果CidrBlock包含您的账户内的云服务器之外的设备在腾讯云的内网IP，并不代表此规则允许您访问这些设备，租户之间网络隔离规则优先于安全组中的内网规则。\n* SecurityGroupId字段允许输入与待修改的安全组位于相同项目中的安全组ID，包括这个安全组ID本身，代表安全组下所有云服务器的内网IP。使用这个字段时，这条规则用来匹配网络报文的过程中会随着被使用的这个ID所关联的云服务器变化而变化，不需要重新修改。\n* Port字段允许输入一个单独端口号，或者用减号分隔的两个端口号代表端口范围，例如80或8000-8010。只有当Protocol字段是TCP或UDP时，Port字段才被接受。\n* Action字段只允许输入ACCEPT或DROP。\n* CidrBlock, SecurityGroupId, AddressTemplate三者是排他关系，不允许同时输入，Protocol + Port和ServiceTemplate二者是排他关系，不允许同时输入。\n* 一次请求中只能创建单个方向的规则, 如果需要指定索引（PolicyIndex）参数, 多条规则的索引必须一致。"
  },
  "ReplaceRoutes": {
    "params": [
      {
        "name": "RouteTableId",
        "desc": "路由表实例ID，例如：rtb-azd4dt1c。"
      },
      {
        "name": "Routes",
        "desc": "路由策略对象。只需要指定路由策略ID（RouteId）。"
      }
    ],
    "desc": "本接口（ReplaceRoutes）根据路由策略ID（RouteId）修改指定的路由策略（Route），支持批量修改。"
  },
  "CreateSubnet": {
    "params": [
      {
        "name": "VpcId",
        "desc": "待操作的VPC实例ID。可通过DescribeVpcs接口返回值中的VpcId获取。"
      },
      {
        "name": "SubnetName",
        "desc": "子网名称，最大长度不能超过60个字节。"
      },
      {
        "name": "CidrBlock",
        "desc": "子网网段，子网网段必须在VPC网段内，相同VPC内子网网段不能重叠。"
      },
      {
        "name": "Zone",
        "desc": "子网所在的可用区ID，不同子网选择不同可用区可以做跨可用区灾备。"
      }
    ],
    "desc": "本接口(CreateSubnet)用于创建子网。\n* 创建子网前必须创建好 VPC。\n* 子网创建成功后，子网网段不能修改。子网网段必须在VPC网段内，可以和VPC网段相同（VPC有且只有一个子网时），建议子网网段在VPC网段内，预留网段给其他子网使用。\n* 你可以创建的最小网段子网掩码为28（有16个IP地址），最大网段子网掩码为16（65,536个IP地址）。\n* 同一个VPC内，多个子网的网段不能重叠。\n* 子网创建后会自动关联到默认路由表。"
  }
}