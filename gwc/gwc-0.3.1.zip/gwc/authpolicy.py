# -*- coding: utf-8 -*-

"""
gwc.authpolicy
该模块包含GeneDock AuthPolicy API接口，用于列出用户被授权的工具和工作流信息。
"""

from __future__ import print_function

import re

import gdpy


def list_user_authorized_policy(endpoint, res_account_name, res_user_name, auth, timeout=gdpy.defaults.connect_timeout):
    """
    List user authorized policy with user group API接口, 返回用户被授权信息。

    Args:
        endpoint: 访问域名，如北京区域的域名为cn-beijing-api.genedock.com
        res_account_name: 登录用户的账号名
        res_user_name: 登录用户的用户名
        auth: 用户认证信息的Auth对象

    Returns:
        resp: 请求响应元素

    Raises:
        ServerError/RequestError: 如果获取失败，则抛出来自服务端的异常或请求异常
    """
    url = '/accounts/' + res_account_name + '/users/' + res_user_name + '/authorized_policies/'
    if not endpoint.startswith('http://') and not endpoint.startswith('https://'):
        res_url = 'https://' + endpoint + url
    else:
        res_url = endpoint + url

    req = gdpy.http.Request('GET', auth, res_url)
    resp = gdpy.http.Session().do_request(req, timeout)
    if resp.status // 100 != 2:
        raise gdpy.exceptions.make_exception(resp)

    return resp


def get_workflow_authorizing_accounts(response):
    """
    根据请求响应元素，得到给登录用户授权过工作流的组织账号集合

    Args:
        response: list_user_authorized_policy函数返回的请求响应Body

    Returns:
        workflow_res_accounts: 给登录用户授权过工作流的组织账号集合
    """
    workflow_res_accounts = []
    for item in response:
        if re.match("CUSTOM_WORKFLOW_POLICY_", item['policy_name']):
            workflow_res_accounts.append(item['owner'])
        elif re.match("gd_policy_for_product_", item['policy_name']):
            workflow_res_accounts.append(item['owner'])
    return set(workflow_res_accounts)


def get_tool_authorizing_accounts(response):
    """
    根据请求响应元素，得到给登录用户授权过工具的组织账号集合

    Args:
        response: list_user_authorized_policy函数请求响应Body

    Returns:
        tool_res_accounts: 给登录用户授权过工具的组织账号集合
    """
    tool_res_accounts = []
    for item in response:
        if re.match("gd_policy_for_public_tools", item['policy_name']):
            tool_res_accounts.append(item['owner'])
    return set(tool_res_accounts)
