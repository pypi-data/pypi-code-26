#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import argparse
import os
import platform
import pydoc
import sys
import time
import logging
import re
import yaml

from prettytable import PrettyTable
import requests

import gdpy
from gwc import login
from gwc import authpolicy
from gwc import __version__

try:
    import configparser as ConfigParser
except ImportError:
    import ConfigParser

try:
    input = raw_input
except NameError:
    input = input

CONFIGFILE = os.path.join(os.path.expanduser('~'), '.gwc_configuration')
SECTION = 'Defaults'
ENDPOINT_DICT = {'beijing': 'cn-beijing-api.genedock.com', 'qingdao': 'cn-qingdao-api.genedock.com',
                 'shenzhen': 'cn-shenzhen-api.genedock.com'}
CurrentTime = time.strftime('_%Y_%m_%d_%H_%M_%S', time.localtime())
PROJECTNAME = 'default'
SYSTERMTOOL = ['mapoutput', 'mapinput', 'loaddata', 'storedata']

_logger = login.init_logger()


def read_configuration(configfile):
    """
    读取配置文件，返回endpoint, access_id, access_key, account_name和user_name信息

    Args:
        configfile: 配置文件路径

    Returns:
        endpoint: 访问域名，如北京区域的域名为cn-beijing-api.genedock.com
        access_id: Access Key ID
        access_key: Access Key Secret
        account_name: 登录用户的账号名
        user_name: 登录用户的用户名
    """
    config = ConfigParser.RawConfigParser()
    read_ok = config.read(configfile)
    if not read_ok:
        _logger.warning('No config information. Please config you account information!')
        print('No config information. Please config you account information!', file=sys.stderr)
        print(
            'Using: "gwc config" or "gwc config -e [endpoint] -i [access_id] -k [access_key] -a [account_name] '
            '-u [user_name]".',
            file=sys.stderr)
        sys.exit(1)

    active_section = SECTION
    try:
        endpoint = config.get(active_section, 'endpoint')
        access_id = config.get(active_section, 'access_id')
        access_key = config.get(active_section, 'access_key')
        account_name = config.get(active_section, 'account_name')
        user_name = config.get(active_section, 'user_name')
        access_id = login.decrypt(access_id)
        access_key = login.decrypt(access_key)
    except ConfigParser.NoSectionError as e:
        _logger.warning('Can not find section: "{}" in config file: "{}".'.format(e.section, CONFIGFILE))
        print('Please config your account information.', file=sys.stderr)
        print(
            'Using: "gwc config" or "gwc config -e [endpoint] -i [access_id] -k [access_key] -a [account_name] '
            '-u [user_name]".',
            file=sys.stderr)
        sys.exit(-1)
    except ConfigParser.NoOptionError as e:
        _logger.warning(
            'Can not find option: "{}" in section: "{}" in config file: "{}".'.format(e.option, e.section, CONFIGFILE))
        print('Please config your account information.', file=sys.stderr)
        print(
            'Using: "gwc config" or "gwc config -e [endpoint] -i [access_id] -k [access_key] -a [account_name] '
            '-u [user_name]".',
            file=sys.stderr)
        sys.exit(-1)

    return endpoint, access_id, access_key, account_name, user_name


def setup_configuration(args):
    """
    配置账号登录信息，并保存到本地，提供交互式和非交互式两种配置方式，并可列出当前配置信息

    Args:
        args: 命令行解析的参数项

        args.endpoint: 访问域名，如北京区域的域名为cn-beijing-api.genedock.com（交互式时默认为北京域名）
        args.id: Access Key ID
        args.key: Access Key Secret
        args.account_name: 登录用户的账号名
        args.user_name: 登录用户的用户名
        args.ls: 列出当前配置信息
    """
    if args.ls:
        endpoint, access_id, access_key, account_name, user_name = read_configuration(CONFIGFILE)
        print('Endpoint: {}\nAccess ID: {}\nAccount: {}\nUser: {}'.format(endpoint, access_id, account_name, user_name))
    elif args.endpoint is None and args.id is None and args.key is None and args.account is None:
        try:
            latest_account_name = ''
            latest_user_name = ''
            if os.path.exists(CONFIGFILE):
                _, _, _, latest_account_name, latest_user_name = read_configuration(CONFIGFILE)

            switch_choice = input('Choose region of GeneDock [Optionals: Beijing | Shenzhen, Default is Beijing]:').lower()
            while switch_choice != '' and switch_choice not in ENDPOINT_DICT.keys():
                switch_choice = input('Choose region of GeneDock [Optionals: Beijing | Shenzhen, Default is Beijing]:').lower()
            if switch_choice == '':
                endpoint = ENDPOINT_DICT['beijing']
            elif switch_choice in ENDPOINT_DICT.keys():
                endpoint = ENDPOINT_DICT[switch_choice]

            switch_choice = input('Enter access id [Required]:')
            while switch_choice == '':
                switch_choice = input('Enter access id [Required]:')
            access_id = switch_choice
            access_id = login.encrypt(access_id)

            switch_choice = input('Enter access key [Required]:')
            while switch_choice == '':
                switch_choice = input('Enter access key [Required]:')
            access_key = switch_choice
            access_key = login.encrypt(access_key)

            switch_choice = input(
                'Enter the Account name or use the latest login Account [{}]:'.format(latest_account_name))
            while switch_choice == '' and latest_account_name == '':
                switch_choice = input('Enter the Account name (no latest login Account):')
            if switch_choice == '':
                account_name = latest_account_name
            else:
                account_name = switch_choice

            switch_choice = input('Enter the User name or use the latest login User [{}]:'.format(latest_user_name))
            while switch_choice == '' and latest_user_name == '':
                switch_choice = input('Enter the User name (no latest login User):')
            if switch_choice == '':
                user_name = latest_user_name
            else:
                user_name = switch_choice

            switch_choice = input('Please confirm the configuration is correctly?[ Y/N ]:').upper()
            while switch_choice == '' or switch_choice not in ['Y', 'YES', 'N', 'NO']:
                switch_choice = input('Please confirm the configuration is correctly?[ Y/N ]:').upper()

            if switch_choice in ['YES', 'Y']:
                config = ConfigParser.RawConfigParser()
                if config.has_section(SECTION) is False:
                    config.add_section(SECTION)
                config.set(SECTION, 'endpoint', endpoint)
                config.set(SECTION, 'access_id', access_id)
                config.set(SECTION, 'access_key', access_key)
                config.set(SECTION, 'account_name', account_name)
                config.set(SECTION, 'user_name', user_name)
                with open(CONFIGFILE, 'w') as f:
                    config.write(f)
                _logger.info('Saving the configuration to the file "{}" successfully.'.format(CONFIGFILE))
                print('It is saved successfully!', file=sys.stdout)
            else:
                sys.exit(-1)
        except KeyboardInterrupt:
            print('KeyboardInterrupt', file=sys.stderr)
    elif args.endpoint and args.id and args.key and args.account:
        access_id = login.encrypt(args.id)
        access_key = login.encrypt(args.key)

        config = ConfigParser.RawConfigParser()
        if config.has_section(SECTION) is False:
            config.add_section(SECTION)
        config.set(SECTION, 'endpoint', args.endpoint)
        config.set(SECTION, 'access_id', access_id)
        config.set(SECTION, 'access_key', access_key)
        config.set(SECTION, 'account_name', args.account)
        config.set(SECTION, 'user_name', args.user)
        with open(CONFIGFILE, 'w') as f:
            config.write(f)
        _logger.info('Saving the configuration to the file "{}" successfully.'.format(CONFIGFILE))
        print('It is saved successfully!', file=sys.stdout)
    elif args.endpoint is None or args.id is None or args.key is None or args.account is None:
        _logger.warning('Missing parameters in command-line gwc config.')
        print('Missing parameters in command-line gwc config!', file=sys.stderr)
        print('Using: gwc config -e [endpoint] -i [access_id] -k [access_key] -a [account_name] -u [user_name]',
              file=sys.stderr)
        sys.exit(-1)


def get_configuration(configfile=CONFIGFILE):
    """
    从configfile中获取access_id和access_key，得到用户认证信息的Auth对象，返回API请求所需的相关信息

    Args:
        configfile: 配置文件路径，默认值为本地保存的配置文件

    Returns:
        endpoint: 访问域名
        account_name: 登录用户的账号名
        user_name: 登录用户的用户名
        gd_auth: 用户认证信息的Auth对象
    """
    endpoint, access_id, access_key, account_name, user_name = read_configuration(configfile)
    gd_auth = gdpy.GeneDockAuth(access_id, access_key, verbose=False)

    return endpoint, account_name, user_name, gd_auth


def get_version(operation, name, res_account, project_name=PROJECTNAME, tool_id=None):
    """
    获取工具或工作流的最新版本号/指定工具id的版本号

    Args：
        operation: 'workflow'或'tool'
        name: 工作流名称或工具名称
        res_account: 指定从该账号下获取资源
        tool_id: 工具的 id

    Returns:
        version: 工作流或工具最新版本号/指定工具id的版本号
    """
    endpoint, account_name, user_name, gd_auth = get_configuration()

    version = 1
    try:
        if operation == 'workflow':
            workflow = gdpy.Workflows(gd_auth, endpoint, res_account, project_name)
            resp = workflow.get_workflow(name)
            for item in gdpy.utils.json_loader(resp.response.text).get('workflows'):
                operation_version = item.get('version')
                if operation_version > version:
                    version = operation_version
        elif operation == 'tool':
            tool = gdpy.Tools(gd_auth, endpoint, res_account, project_name)
            resp = tool.get_tool(name)
            for item in gdpy.utils.json_loader(resp.response.text).get('tools'):
                operation_version = item.get('configs').get('version')
                if tool_id:
                    # 传入 tool id 获取指定的版本号
                    if tool_id == item.get('configs').get('_id'):
                        return int(operation_version)
                else:
                    # 没传入 id 就取最新的版本号
                    if operation_version > version:
                        version = operation_version
            # 这里表示此账号下的 tools 没有对应的 tool_id
            if tool_id:
                return None
        _logger.info(
            'Get {} latest version successfully! name: {}, version: {}, resource account: {}.'.format(operation, name,
                                                                                                      version,
                                                                                                      res_account))
        return int(version)
    except gdpy.exceptions.RequestError as e:
        _logger.warning('Get {} latest version failed! status: {}, error: {}'.format(operation, e.status,
                                                                                     e.error_message.decode('utf-8')))
        print('Get {} latest version failed!\nstatus: {}\nerror: {}'.format(operation, e.status,
                                                                            e.error_message.decode('utf-8')),
              file=sys.stderr)
        print('NetWork Connection Error, please check your network and retry.', file=sys.stderr)
        sys.exit(-1)
    except gdpy.exceptions.ServerError as e:
        if e.status // 100 == 4:
            # 在调用的地方处理 None 的情况
            return None
        _logger.warning('Get {} latest version failed! status: {}, error: {}, 错误: {}'.format(
            operation, e.status, e.error_message.decode('utf-8'), e.error_message_chs.decode('utf-8')))
        print('Get {} latest version failed!\nstatus: {}\nerror: {}\n错误: {}'.format(
            operation, e.status, e.error_message.decode('utf-8'), e.error_message_chs.decode('utf-8')), file=sys.stderr)
        if e.status // 100 == 5:
            print('Please retry, if failed again, contact with the staff of GeneDock.', file=sys.stderr)
        sys.exit(-1)
    except ValueError as e:
        _logger.warning('Get {} latest version failed! error: {}'.format(operation, e))
        print('Get {} latest version failed!\nerror: {}'.format(operation, e), file=sys.stderr)
        print('Please check the input "{} name".'.format(operation), file=sys.stderr)
        sys.exit(-1)


def gdpy_operation(func, *args, **kwargs):
    """gdpy 操作
    :param func: gdpy的func
    :param args: func的位置参数
    :param kwargs:
        action: gdpy操作
        input_info: 当404报错时，需要检查的内容
    :return:
    """
    action = kwargs.pop('action')

    try:
        return func(*args, **kwargs)
    except gdpy.exceptions.RequestError as e:
        _logger.warning(
            'Failed to %s! status: %s, error: %s\nNetWork Connection Error, please check your network and retry.'
            , action, e.status, e.error_message.decode('utf-8'))
        print('Failed to {}!\nstatus: {}\nerror: {}\n'.format(action, e.status, e.error_message.decode(
            'utf-8')), file=sys.stderr)
        print('NetWork Connection Error, please check your network and retry.', file=sys.stderr)
        os._exit(-1)
    except gdpy.exceptions.ServerError as e:
        if e.status == 404:
            return None  # 函数调用的地方对这个做处理
        _logger.warning('Failed to %s! status: %s, error: %s, 错误: %s', action, e.status,
                        e.error_message.decode('utf-8'),
                        e.error_message_chs.decode('utf-8'))
        print('Failed to {}!\nstatus: {}\nerror: {}\n错误: {}'.format(action, e.status,
                                                                    e.error_message.decode('utf-8'),
                                                                    e.error_message_chs.decode('utf-8')),
              file=sys.stderr)
        if e.status // 100 == 5:
            print('Please retry, if failed again, contact with the staff of GeneDock.', file=sys.stderr)
            os._exit(-1)
    except ValueError as e:
        _logger.warning('Failed to %s! error: %s', action, e)
        print('Failed to {}!\nerror: {}'.format(action, e), file=sys.stderr)
        os._exit(-1)


def get_job_integral_log(log_downloadurl, job_id):
    """获取job日志全部内容
    :param log_downloadurl: job日志存放地址
    :param job_id: job id
    :return:
    """
    try:
        resp = requests.get(log_downloadurl)
    except requests.exceptions.HTTPError as err:
        print('Failed to get job ({}) log!\nerror: {}\n'.format(job_id, err, file=sys.stderr))
        print('NetWork Connection Error, please check your network and retry.', file=sys.stderr)
        os._exit(-1)

    if 200 <= resp.status_code < 300:
        return resp.text
    else:
        print('Failed to get job ({}) log!'.format(job_id), file=sys.stderr)
        print(resp.text, file=sys.stderr)
        os._exit(-1)


def _get_jobs_info(task_id, quiet):
    """
    :param task_id: task id
    :param quiet: boolean值，true表示只返回 job id
    :return:
    """
    endpoint, account_name, user_name, gd_auth = get_configuration()
    task = gdpy.Tasks(gd_auth, endpoint, account_name, PROJECTNAME)
    resp = gdpy_operation(task.get_jobs, task_id, action='get jobs log')
    if resp is None:
        print('Please check the input "task id".', file=sys.stderr)
        os._exit(-1)
    table = json2table(resp.response.text, "jobs", ["job_id", "app_name", "status", "startTime", "endTime"], 1)
    if quiet:
        table.header = False
        _logger.info(table.get_string(fields=["job_id"], start=0))
        jobsid_str = table.get_string(fields=["job_id"], start=0)
        jobsid_list = jobsid_str.split()
        print("\n".join(jobsid_list))
        return jobsid_list
    else:
        _logger.info('Get jobs info successfully! task_id: %s.', task_id)
        print(table)


def get_jobs_info(args):
    """
    列出指定task下的job信息

    Args:
        args: 命令行解析的参数项

        args.taskid: 指定task id
        args.quiet: 逻辑值，是否只是显示 job id
    """

    task_id = args.taskid
    quiet = args.quiet

    _get_jobs_info(task_id, quiet)


def get_job_cmd(args):
    """
    列出指定job运行时的command

    Args:
        args: 命令行解析的参数项

        args.jobid: 指定job id
    """
    endpoint, account_name, user_name, gd_auth = get_configuration()

    task = gdpy.Tasks(gd_auth, endpoint, account_name, PROJECTNAME)
    job_id = args.jobid

    try:
        resp = task.get_job_cmd(job_id)
        job_cmd = gdpy.utils.json_loader(resp.response.text)
        job_cmd = gdpy.yml_utils.yaml_dumper(job_cmd)
        _logger.info('Get job command successfully! job id: {}.'.format(job_id))
        print(job_cmd.decode('utf-8'), file=sys.stdout)
    except gdpy.exceptions.RequestError as e:
        _logger.warning(
            'Failed to get the job command! status: {}, error: {}'.format(e.status, e.error_message.decode('utf-8')))
        print('Failed to get the job command!\nstatus: {}\nerror: {}\n'.format(
            e.status, e.error_message.decode('utf-8')), file=sys.stderr)
        print('NetWork Connection Error, please check your network and retry.', file=sys.stderr)
    except gdpy.exceptions.ServerError as e:
        _logger.warning('Failed to get the job command! status: {}, error: {}, 错误: {}'.format(
            e.status, e.error_message.decode('utf-8'), e.error_message_chs.decode('utf-8')))
        print('Failed to get the job command!\nstatus: {}\nerror: {}\n错误: {}'.format(
            e.status, e.error_message.decode('utf-8'), e.error_message_chs.decode('utf-8')), file=sys.stderr)
        if e.status // 100 == 5:
            print('Please retry, if failed again, contact with the staff of GeneDock.', file=sys.stderr)
        elif e.status // 100 == 4:
            print('Please check the input "job id" or whether you have permission to get the tool\'s cmd.',
                  file=sys.stderr)


def get_job_log(args):
    """获取指定job的日志信息
    :param args: 命令行解析参数

                args.jobid: 指定job id
                args.output: job日志文件输出路径 （不填默认输出到屏幕）
    """
    endpoint, account_name, user_name, gd_auth = get_configuration()

    task = gdpy.Tasks(gd_auth, endpoint, account_name, PROJECTNAME)
    job_id = args.jobid
    try:
        resp = task.get_job_info(job_id)
        job_info = gdpy.utils.json_loader(resp.response.text)
        job_log = get_job_integral_log(job_info["Log_downloadURL"], job_info["job_id"])
        if args.output:
            with open(args.output, 'w') as f:
                f.write(job_log)
            _logger.info('Get job(%s) log successfully! The output was saved to the file %s', job_id, args.output)
            print('Get job({}) log successfully! The output was saved to the file {}'.format(job_id, args.output))
        else:
            _logger.info('Get job(%s) log successfully!', job_id)
            print('Get job({}) log successfully!'.format(job_id))
            print(job_log.decode('utf-8'))
    except gdpy.exceptions.RequestError as e:
        _logger.warning(
            'Failed to get log! status: %s, error: %s\nNetWork Connection Error, please check your network and retry.'
            , e.status, e.error_message.decode('utf-8'))
    except gdpy.exceptions.ServerError as e:
        _logger.warning('Failed to get log! status: %s, error: %s, 错误: %s', e.status, e.error_message.decode('utf-8'),
                        e.error_message_chs.decode('utf-8'))
        if e.status // 100 == 5:
            _logger.warning('Please retry, if failed again, contact with the staff of GeneDock.')
        elif e.status // 100 == 4:
            _logger.warning('Please check the input "job id" or whether you have permission to get log.')


def delete_task(args):
    """
    删除task

    Args:
        args: 命令行解析的参数项

        args.taskid: 指定task id
    """
    endpoint, account_name, user_name, gd_auth = get_configuration()

    task = gdpy.Tasks(gd_auth, endpoint, account_name, PROJECTNAME)
    task_id = args.taskid

    try:
        resp = task.delete_task(task_id)
        _logger.info('Deleting task successfully! task id: {}'.format(task_id))
        print('Deleting task successfully! task id: {}'.format(task_id), file=sys.stdout)
    except gdpy.exceptions.RequestError as e:
        _logger.warning(
            'Failed to delete the task! status: {}, error: {}'.format(e.status, e.error_message.decode('utf-8')))
        print('Failed to delete the task!\nstatus: {}\nerror: {}\n'.format(
            e.status, e.error_message.decode('utf-8')), file=sys.stderr)
        print('NetWork Connection Error, please check your network and retry.', file=sys.stderr)
    except gdpy.exceptions.ServerError as e:
        _logger.warning('Failed to delete the task! status: {}, error: {}, 错误: {}'.format(
            e.status, e.error_message.decode('utf-8'), e.error_message_chs.decode('utf-8')))
        print('Failed to delete the task!\nstatus: {}\nerror: {}\n错误: {}'.format(
            e.status, e.error_message.decode('utf-8'), e.error_message_chs.decode('utf-8')), file=sys.stderr)
        if e.status // 100 == 5:
            print('Please retry, if failed again, contact with the staff of GeneDock.', file=sys.stderr)
        elif e.status // 100 == 4:
            print('Please check the input "task id".', file=sys.stderr)


def get_task(args):
    """
    获取指定task运行状态信息

    Args:
        args: 命令行解析的参数项

        args.taskid: 指定task id
    """
    endpoint, account_name, user_name, gd_auth = get_configuration()

    task = gdpy.Tasks(gd_auth, endpoint, account_name, PROJECTNAME)
    task_id = args.taskid

    try:
        resp = task.get_task(task_id)
        task_info = gdpy.utils.json_loader(resp.response.text)
        task_info = gdpy.yml_utils.yaml_dumper(task_info)
        _logger.info('Get task successfully! task id: {}.'.format(task_id))
        print(task_info.decode('utf-8'), file=sys.stdout)
    except gdpy.exceptions.RequestError as e:
        _logger.warning(
            'Failed to get the task! status: {}, error: {}'.format(e.status, e.error_message.decode('utf-8')))
        print('Failed to get the task!\nstatus: {}\nerror: {}\n'.format(
            e.status, e.error_message.decode('utf-8')), file=sys.stderr)
        print('NetWork Connection Error, please check your network and retry.', file=sys.stderr)
    except gdpy.exceptions.ServerError as e:
        _logger.warning('Failed to get the task! status: {}, error: {}, 错误: {}'.format(
            e.status, e.error_message.decode('utf-8'), e.error_message_chs.decode('utf-8')))
        print('Failed to get the task!\nstatus: {}\nerror: {}\n错误: {}'.format(
            e.status, e.error_message.decode('utf-8'), e.error_message_chs.decode('utf-8')), file=sys.stderr)
        if e.status // 100 == 5:
            print('Please retry, if failed again, contact with the staff of GeneDock.', file=sys.stderr)
        elif e.status // 100 == 4:
            print('Please check the input "task id".', file=sys.stderr)


def list_task(args):
    """
    列出task的状态信息

    Args:
        args: 命令行解析的参数项

        args.size: task记录返回的最大条目，默认500
        args.fromdate: 查询开始时间点，格式为：%Y-%m-%d，代表：%Y-%m-%d 00:00:00，默认为查询结束时间的7天前
        args.todate: 查询结束时间点，格式为：%Y-%m-%d，代表：%Y-%m-%d 00:00:00，默认为当前时间
        args.ts: 默认时间格式: 2018-06-04 16:22:28, 加上参数后变成时间戳格式
    """
    endpoint, account_name, user_name, gd_auth = get_configuration()

    task = gdpy.Tasks(gd_auth, endpoint, account_name, PROJECTNAME)

    if args.todate:
        try:
            to_date = gdpy.utils.iso8601_to_unixtime(args.todate + 'T0:0:0.000Z') - 60 * 60 * 8
        except ValueError as e:
            _logger.warning('Error: time data {} does not match format "%Y-%m-%d".'.format(args.todate))
            print('Error: time data {} does not match format "%Y-%m-%d".'.format(args.todate))
            print('Please check the input "todate", format: "%Y-%m-%d".')
            sys.exit(-1)
    else:
        to_date = int(time.time())

    if args.fromdate:
        try:
            from_date = gdpy.utils.iso8601_to_unixtime(args.fromdate + 'T0:0:0.000Z') - 60 * 60 * 8
        except ValueError as e:
            _logger.warning('Error: time data {} does not match format "%Y-%m-%d".'.format(args.fromdate))
            print('Error: time data {} does not match format "%Y-%m-%d".'.format(args.fromdate))
            print('Please check the input "fromdate", format: "%Y-%m-%d".')
            sys.exit(-1)
    else:
        from_date = to_date - 60 * 60 * 24 * 7

    try:
        resp = task.list_tasks(params={'size': args.size, 'from': from_date, 'to': to_date})
        tasks_info = gdpy.utils.json_loader(resp.response.text)
        for task_info in tasks_info['task_list']:
            task_info['user_name'] = task_info.pop('user')
            if args.totimestamp:
                continue
            start_time = task_info['startTime']
            task_info['startTime'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_time))
            end_time = task_info['endTime']
            if end_time is not None:
                task_info['endTime'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(end_time))

        task_json = gdpy.utils.json_dumper(tasks_info)
        table = json2table(task_json, 'task_list', ['task_id', 'user_name', 'task_name', 'status', 'process', 'startTime',
                                                    'endTime', 'workflow_name', 'workflow_version'], None)
        _logger.info('Listing task successfully!')
        if platform.system() == 'Windows':
            print('Total tasks: {}, Count tasks: {}\n{}'.format(resp.total, len(resp.task_list), table))
        else:
            pydoc.pipepager('Total tasks: {}, Count tasks: {}\n{}'.format(resp.total, len(resp.task_list), str(table)),
                            cmd='less -M -S')
    except gdpy.exceptions.RequestError as e:
        _logger.warning(
            'Failed to list the task! status: {}, error: {}'.format(e.status, e.error_message.decode('utf-8')))
        print('Failed to list the task!\nstatus: {}\nerror: {}\n'.format(
            e.status, e.error_message.decode('utf-8')), file=sys.stderr)
        print('NetWork Connection Error, please check your network and retry.', file=sys.stderr)
    except gdpy.exceptions.ServerError as e:
        _logger.warning('Failed to list the task! status: {}, error: {}, 错误: {}'.format(
            e.status, e.error_message.decode('utf-8'), e.error_message_chs.decode('utf-8')))
        print('Failed to list the task!\nstatus: {}\nerror: {}\n错误: {}'.format(
            e.status, e.error_message.decode('utf-8'), e.error_message_chs.decode('utf-8')), file=sys.stderr)
        if e.status // 100 == 5:
            print('Please retry, if failed again, contact with the staff of GeneDock.', file=sys.stderr)
        elif e.status // 100 == 4:
            print('Please check the input "task id".', file=sys.stderr)


def stop_task(args):
    """
    停止task

    Args:
        args: 命令行解析的参数项

        args.taskid: 指定task id
    """
    endpoint, account_name, user_name, gd_auth = get_configuration()

    task = gdpy.Tasks(gd_auth, endpoint, account_name, PROJECTNAME)
    task_id = args.taskid

    try:
        resp = task.stop_task(task_id)
        _logger.info('Stopping task successfully! task id: {}'.format(task_id))
        print('Stopping task successfully! task id: {}'.format(task_id), file=sys.stdout)
    except gdpy.exceptions.RequestError as e:
        _logger.warning(
            'Failed to stop the task! status: {}, error: {}'.format(e.status, e.error_message.decode('utf-8')))
        print('Failed to stop the task!\nstatus: {}\nerror: {}\n'.format(
            e.status, e.error_message.decode('utf-8')), file=sys.stderr)
        print('NetWork Connection Error, please check your network and retry.', file=sys.stderr)
    except gdpy.exceptions.ServerError as e:
        _logger.warning('Failed to stop the task! status: {}, error: {}, 错误: {}'.format(
            e.status, e.error_message.decode('utf-8'), e.error_message_chs.decode('utf-8')))
        print('Failed to stop the task!\nstatus: {}\nerror: {}\n错误: {}'.format(
            e.status, e.error_message.decode('utf-8'), e.error_message_chs.decode('utf-8')), file=sys.stderr)
        if e.status // 100 == 5:
            print('Please retry, if failed again, contact with the staff of GeneDock.', file=sys.stderr)
        elif e.status // 100 == 4:
            print('Please check the input "task id".', file=sys.stderr)


def get_jobs_log(args):
    """获取 task 下面所有job的日志
    Args:
        args: 命令行解析的参数项
        args.taskid: 指定task id
    """
    endpoint, account_name, user_name, gd_auth = get_configuration()

    # 获取 task 下面的 jobs id
    task = gdpy.Tasks(gd_auth, endpoint, account_name, PROJECTNAME)
    task_id = args.taskid
    resp = gdpy_operation(task.get_jobs, task_id, action='get jobs log')
    if resp is None:
        print('Please check the input "task id".', file=sys.stderr)
        os._exit(-1)
    table = json2table(resp.response.text, "jobs", ["job_id", "app_name", "status", "startTime", "endTime"], 1)
    jobsid = table.get_string(fields=["job_id"], start=0).split()[1:]
    for jobid in jobsid:
        # 获取 job id
        resp = gdpy_operation(task.get_job_info, jobid, action='get job log')
        if resp is None:
            print('Get job: {} log fail'.format(jobid), file=sys.stderr)
            continue
        job_info = gdpy.utils.json_loader(resp.response.text)
        job_log = get_job_integral_log(job_info["Log_downloadURL"], job_info["job_id"])
        log_dir = '{}/{}'.format(task_id, jobid)
        if os._exists(log_dir):
            pass
        else:
            os.makedirs(log_dir)
        job_log_path = '{}/stdout.log'.format(log_dir)
        with open(job_log_path, 'w') as f:
            f.write(job_log)
        _logger.info('Get job(%s) log successfully! The output was saved to the file %s', jobid, job_log_path)
        print('Get job({}) log successfully! The output was saved to the file {}'.format(jobid, job_log_path))


def _create_tool(tool_name, configs, version):
    """创建工具
    :param tool_name: 工具名字
    :param configs: 工具配置文件地址
    :param version: 工具版本
    :return:
    """
    endpoint, account_name, user_name, gd_auth = get_configuration()

    tool = gdpy.Tools(gd_auth, endpoint, account_name, PROJECTNAME)

    if version is None:
        version = get_version('tool', tool_name, account_name, project_name=PROJECTNAME)
        _logger.info('Get workflow latest version successfully! name: %s, version: %s', tool_name, version)
        tool_version = 1
        if version is not None:
            tool_version = int(version) + 1
    else:
        tool_version = version

    if os.path.exists(configs):
        try:
            tool_temp = gdpy.yml_utils.yaml_loader(configs)
            tool_temp['app']['name'] = tool_name
            tool_temp['app']['version'] = tool_version
            tool_temp = gdpy.yml_utils.yaml_dumper(tool_temp)
        except (AttributeError, KeyError):
            print('Invalid config file! Please check "app" elements in the config file')
            sys.exit(-1)
    else:
        print('{} file not exists!'.format(configs))
        sys.exit(-1)

    with open(configs + '_tmp.yml', 'w') as f:
        f.write(tool_temp.decode('utf-8'))

    resp = gdpy_operation(tool.create_tool, tool_name, tool_version, action='create tool')
    if resp is None:
        print('Please check the input "tool name" or "tool version".')
        os._exit(-1)

    resp = gdpy_operation(tool.put_tool, configs + '_tmp.yml', action='put tool')
    if resp is None:
        print('Please check the input "tool name" or "tool version".')
        os._exit(-1)

    os.remove(configs + '_tmp.yml')


def create_tool(args):
    """
    创建工具

    Args:
        args: 命令行解析的参数项

        args.name: 工具名称
        args.configs: 工具配置文件
        args.version: 工具版本（不填默认为1，后面版本自动加1）
    """
    tool_name = args.name
    configs = args.configs
    version = args.version
    _create_tool(tool_name, configs, version)


def delete_tool(args):
    """
    删除工具

    Args:
        args: 命令行解析的参数项

        args.name: 工具名称
        args.version: 工具版本（不填默认为最新版本）
    """
    endpoint, account_name, user_name, gd_auth = get_configuration()

    tool_name = args.name

    if args.version is None:
        tool_version = get_version('tool', tool_name, account_name, PROJECTNAME)
        if tool_version is None:
            print('Please check the input "tool name" or "resource account" (if authoried by others).')
            os._exit(1)
    else:
        tool_version = args.version

    tool = gdpy.Tools(gd_auth, endpoint, account_name, PROJECTNAME)
    try:
        resp = tool.delete_tool(tool_name, tool_version)
        _logger.info('Deleting tool successfully! name: {}, version: {}.'.format(tool_name, tool_version))
        print('Deleting tool successfully! name: {}, version: {}.'.format(tool_name, tool_version), file=sys.stdout)
    except gdpy.exceptions.RequestError as e:
        _logger.warning(
            'Failed to delete the tool! status: {}, error: {}'.format(e.status, e.error_message.decode('utf-8')))
        print('Failed to delete the tool!\nstatus: {}\nerror: {}\n'.format(
            e.status, e.error_message.decode('utf-8')), file=sys.stderr)
        print('NetWork Connection Error, please check your network and retry.', file=sys.stderr)
    except gdpy.exceptions.ServerError as e:
        _logger.warning('Failed to delete the tool! status: {}, error: {}, 错误: {}'.format(
            e.status, e.error_message.decode('utf-8'), e.error_message_chs.decode('utf-8')))
        print('Failed to delete the tool!\nstatus: {}\nerror: {}\n错误: {}'.format(
            e.status, e.error_message.decode('utf-8'), e.error_message_chs.decode('utf-8')), file=sys.stderr)
        if e.status // 100 == 5:
            print('Please retry, if failed again, contact with the staff of GeneDock.', file=sys.stderr)
        elif e.status // 100 == 4:
            print('Please check the content of the input "tool name" or "tool version".', file=sys.stderr)
    except ValueError as e:
        _logger.warning('Failed to delete the tool! error: {}'.format(e))
        print('Failed to delete the tool!\nerror: {}'.format(e), file=sys.stderr)
        print('Please check the input "tool name" or "tool version".', file=sys.stderr)


def _get_tool(tool_name, version, output, isreturnid=False):
    """获取工具配置文件
    :param tool_name: 工具名字
    :param version: 工具版本
    :param output: 工具输出文件
    :param isreturnid: 只是获取id
    :return:
    """
    endpoint, account_name, user_name, gd_auth = get_configuration()

    if version is None:
        tool_version = get_version('tool', tool_name, account_name, PROJECTNAME)
        if tool_version is None:
            return None
    else:
        tool_version = version

    tool = gdpy.Tools(gd_auth, endpoint, account_name, PROJECTNAME)
    resp = gdpy_operation(tool.get_tool, tool_name, tool_version, action='get tool')
    if resp is None:
        return None

    tool_config = gdpy.utils.json_loader(resp.response.text)

    # 系统工具不能下载
    tools = tool_config.get('tools', [])
    if len(tools) > 0 and tools[0].get('config', {}).get('type') == 'system':
        print("Permission denied to get app: {}, "
              "it's a SYSTEM APP ... pass".format(tool_config['tools'][0]['configs']['_id']))
        return

    tool_id = tool_config['tools'][0]['configs']['_id']
    tool_config['app'] = tool_config['tools'][0]['configs']
    del tool_config['tools']
    del tool_config['app']['_id']
    tool_config = gdpy.yml_utils.yaml_dumper(tool_config).decode('utf-8')

    if isreturnid:
        return tool_id

    if output:
        with open(output, 'w') as f:
            f.write(tool_config)
        _logger.info('Get tool successfully! name: %s, version: %s. The output was saved to the file "%s"!',
            tool_name, tool_version, output)
        print('Get tool: {} (version: {}) successfully! '
              'The output was saved to the file "{}"!'.format(tool_name, tool_version, output))
    else:
        _logger.info('Get tool successfully! name: %s, version: %s.', tool_name, tool_version)
        print(tool_config)


def get_tool(args):
    """
    下载工具配置文件

    Args：
        args: 命令行解析的参数项

        args.name: 工具名称
        args.version: 工具版本（不填默认为最新版本）
        args.output: 配置文件输出路径（不填默认输出到屏幕）
    """

    tool_name = args.name
    version = args.version
    output = args.output
    resp = _get_tool(tool_name, version, output)
    if resp is None:
        print('Please check the input "tool name" or "tool version".')


def list_tool(args):
    """
    列出自己创建的工具和被授权的工具

    Args：
        args: 命令行解析的参数项

        args.account: 工具所属的资源账号，不加该参数项时，输出所有有权限的工具
    """
    endpoint, account_name, user_name, gd_auth = get_configuration()

    if args.account is None:
        tool_res_accounts = [account_name]
        try:
            resp = authpolicy.list_user_authorized_policy(endpoint, account_name, user_name, gd_auth)
            authorized_info = gdpy.utils.json_loader(resp.response.text)
            tool_res_accounts.extend(authpolicy.get_tool_authorizing_accounts(authorized_info))
            tool_res_accounts = set(tool_res_accounts)
            _logger.info('Listing user authorized policy successfully!')
        except gdpy.exceptions.RequestError as e:
            _logger.warning('Failed to list user authorized policy! '
                            'status: {}, error: {}'.format(e.status, e.error_message.decode('utf-8')))
            print('Failed to list user authorized policy!\nstatus: {}\nerror: {}\n'.format(
                e.status, e.error_message.decode('utf-8')), file=sys.stderr)
            print('NetWork Connection Error, please check your network and retry.', file=sys.stderr)
            sys.exit(-1)
        except gdpy.exceptions.ServerError as e:
            _logger.warning('Failed to list user authorized policy! status: {}, error: {}, 错误: {}'.format(
                e.status, e.error_message.decode('utf-8'), e.error_message_chs.decode('utf-8')))
            print('Failed to list user authorized policy!\nstatus: {}\nerror: {}\n错误: {}'.format(
                e.status, e.error_message.decode('utf-8'), e.error_message_chs.decode('utf-8')), file=sys.stderr)
            if e.status // 100 == 5:
                print('Please retry, if failed again, contact with the staff of GeneDock.', file=sys.stderr)
            elif e.status // 100 == 4:
                print('Please check the configuration info.', file=sys.stderr)
            sys.exit(-1)
    else:
        tool_res_accounts = [args.account]

    tool_template = []
    for res_account_name in tool_res_accounts:
        tool = gdpy.Tools(gd_auth, endpoint, res_account_name, PROJECTNAME)
        try:
            resp = tool.list_tools()
            for item in resp.tools:
                for tool_item in item:
                    tool_item['tool_account'] = res_account_name
                tool_template.append(item)
            _logger.info('Listing tool successfully! res_account: {}.'.format(res_account_name))
        except gdpy.exceptions.RequestError as e:
            _logger.warning(
                'Failed to list the tool! status: {}, error: {}'.format(e.status, e.error_message.decode('utf-8')))
            print('Failed to list the tool!\nstatus: {}\nerror: {}\n'.format(
                e.status, e.error_message.decode('utf-8')), file=sys.stderr)
            print('NetWork Connection Error, please check your network and retry.', file=sys.stderr)
        except gdpy.exceptions.ServerError as e:
            _logger.warning('Failed to list the tool!\nstatus: {}, error: {}, 错误: {}'.format(
                e.status, e.error_message.decode('utf-8'), e.error_message_chs.decode('utf-8')))
            if e.status // 100 == 5:
                print('Please retry, if failed again, contact with the staff of GeneDock.', file=sys.stderr)
            else:
                continue

    if tool_template:
        table = json2table(gdpy.utils.json_dumper({'tools': tool_template}), 'tools',
                           ['tool_name', 'tool_version', 'tool_account', 'tool_id', 'category', 'status'], None)
        print(table, file=sys.stdout)
    else:
        print('Failed to list the tool!', file=sys.stderr)
        print('Please check the input "resource account name".', file=sys.stderr)


def update_tool(args):
    """
    更新工具配置文件

    Args：
        args: 命令行解析的参数项

        args.name: 工具名称
        args.configs: 工具配置文件
        args.version: 工具版本（不填默认为最新版本）
    """
    endpoint, account_name, user_name, gd_auth = get_configuration()

    tool_name = args.name

    if args.version is None:
        tool_version = get_version('tool', tool_name, account_name, PROJECTNAME)
        if tool_version is None:
            print('Please check the input "tool name" or "resource account" (if authoried by others).')
            os._exit(1)
    else:
        tool_version = args.version

    if os.path.exists(args.configs):
        try:
            tool_temp = gdpy.yml_utils.yaml_loader(args.configs)
            if tool_name != tool_temp.get('app').get('name'):
                print('The input tool name is not consistent with the name in the input config file.'.format(tool_name),
                      file=sys.stderr)
                print('Please check the input "tool name" or the "name" in the input config file', file=sys.stderr)
                sys.exit(-1)
            if tool_version != tool_temp.get('app').get('version'):
                print(
                    'The input tool version (default: latest version) is not consistent with the version '
                    'in the input config file.',
                    file=sys.stderr)
                print('Please check the input "tool version" or the "version" in the input config file!',
                      file=sys.stderr)
                sys.exit(-1)
        except (AttributeError, KeyError):
            print('Invalid config file! Please check "app", "name", "version" elements in the config file',
                  file=sys.stderr)
            sys.exit(-1)
    else:
        print('{} file not exists!'.format(args.configs), file=sys.stderr)
        sys.exit(-1)

    tool = gdpy.Tools(gd_auth, endpoint, account_name, PROJECTNAME)
    try:
        resp = tool.put_tool(args.configs)
        _logger.info('Updating tool successfully! name: {}, version: {}.'.format(tool_name, tool_version))
        print('Updating tool successfully! name: {}, version: {}.'.format(tool_name, tool_version), file=sys.stdout)
    except gdpy.exceptions.RequestError as e:
        _logger.warning(
            'Failed to update the tool! status: {}, error: {}'.format(e.status, e.error_message.decode('utf-8')))
        print('Failed to update the tool!\nstatus: {}\nerror: {}\n'.format(
            e.status, e.error_message.decode('utf-8')), file=sys.stderr)
        print('NetWork Connection Error, please check your network and retry.', file=sys.stderr)
    except gdpy.exceptions.ServerError as e:
        _logger.warning('Failed to update the tool! status: {}, error: {}, 错误: {}'.format(
            e.status, e.error_message.decode('utf-8'), e.error_message_chs.decode('utf-8')))
        print('Failed to update the tool!\nstatus: {}\nerror: {}\n错误: {}'.format(
            e.status, e.error_message.decode('utf-8'), e.error_message_chs.decode('utf-8')), file=sys.stderr)
        if e.status // 100 == 5:
            print('Please retry, if failed again, contact with the staff of GeneDock.', file=sys.stderr)
        elif e.status // 100 == 4:
            print(
                'Please check the content of the input "config file" or use "gwc tool get" command to obtain '
                'the tool original configuration file and remodify it',
                file=sys.stderr)
    except ValueError as e:
        _logger.warning('Failed to update the tool! error: {}'.format(e))
        print('Failed to update the tool!\nerror: {}'.format(e), file=sys.stderr)
        print('Please check the input "tool name" or "tool version".', file=sys.stderr)


def active_workflow(args):
    """
    运行工作流

    Args:
        args: 命令行解析的参数项

        args.name: 工作流名称
        args.parameters: 工作流运行所需的配置文件（配置文件中输入项数据的名称必须填写）
        args.account: 工作流账号归属（不填默认为当前账号，如需获取公共资源，则为public）
        args.task: 指定Task名称（不填则为系统默认生成名称）
        args.version: 工作流版本（不填默认以最新版本运行）
    """
    endpoint, account_name, user_name, gd_auth = get_configuration()

    workflow_name = args.name

    if args.account:
        workflow_owner = args.account
    else:
        workflow_owner = account_name

    if args.version:
        workflow_version = args.version
    else:
        workflow_version = get_version('workflow', workflow_name, workflow_owner, PROJECTNAME)
        if workflow_version is None:
            print('Please check the input "workflow name" or "resource account" (if authoried by others).')
            os._exit(1)

    workflow_param_file = args.parameters
    workflow_param = gdpy.yml_utils.yaml_loader(workflow_param_file)

    if args.task:
        task_name = args.task
    else:
        task_name = workflow_name + CurrentTime
    workflow_param['name'] = task_name
    workflow_param['Property']['reference_task'][0]['id'] = 'null'

    for node in workflow_param['Outputs']:
        node_info = workflow_param['Outputs'][node]
        out_data_name = node_info['data'][0]['name']
        out_data_format = node_info['formats'][0]
        if out_data_name == '<Please input the name of the output data in here>' or out_data_name is None or out_data_name == '':
            out_data_name = '/home/' + user_name + '/' + task_name + '/' + node + '.' + out_data_format
            node_info['data'][0]['name'] = out_data_name

    workflow_param = gdpy.yml_utils.yaml_dumper(workflow_param)
    with open(task_name + '_tmp.yml', 'w') as f:
        f.write(workflow_param.decode('utf-8'))

    task = gdpy.Tasks(gd_auth, endpoint, account_name, PROJECTNAME, connect_timeout=3600)
    try:
        resp = task.active_workflow(task_name + '_tmp.yml', workflow_name, workflow_version, workflow_owner)
        _logger.info('Run the workflow successfully! name: {}, version: {}. task_name: {}, task_id: {}'.format(
            workflow_name, workflow_version, resp.task_name, resp.task_id))
        print('Run the workflow successfully!\ntask_name: {}, task_id: {}'.format(resp.task_name, resp.task_id),
              file=sys.stdout)
    except gdpy.exceptions.RequestError as e:
        _logger.warning(
            'Failed to active the workflow! status: {}, error: {}'.format(e.status, e.error_message.decode('utf-8')))
        print('Failed to active the workflow!\nstatus: {}\nerror: {}'.format(e.status, e.error_message.decode('utf-8')),
              file=sys.stderr)
        print('NetWork Connection Error, please check your network and retry.', file=sys.stderr)
    except gdpy.exceptions.ServerError as e:
        _logger.warning('Failed to active the workflow! status: {}, error: {}, 错误: {}'.format(
            e.status, e.error_message.decode('utf-8'), e.error_message_chs.decode('utf-8')))
        print('Failed to active the workflow!\nstatus: {}\nerror: {}\n错误: {}'.format(
            e.status, e.error_message.decode('utf-8'), e.error_message_chs.decode('utf-8')), file=sys.stderr)
        if e.status // 100 == 5:
            print('Please retry, if failed again, contact with the staff of GeneDock.')
        elif e.status // 100 == 4:
            print(
                'Please check the input "workflow name", "workflow version", "the inputs data name in parameters file" '
                'or "resource account" (if authoried by others).')
    except ValueError as e:
        _logger.warning('Failed to active the workflow! error: {}'.format(e))
        print('Failed to active the workflow!\nerror: {}'.format(e), file=sys.stderr)
        print('Please check the input "workflow name" or "workflow version".', file=sys.stderr)

    os.remove(task_name + '_tmp.yml')


def _create_workflow(workflow_name, configs, version):
    """创建工作流
    :param workflow_name: 工作流名字
    :param configs: 工作流配置文件路径
    :param version: 工作流版本
    :return:
    """
    endpoint, account_name, user_name, gd_auth = get_configuration()
    workflow = gdpy.Workflows(gd_auth, endpoint, account_name, PROJECTNAME)
    if version is None:
        version = get_version('workflow', workflow_name, account_name, project_name=PROJECTNAME)
        _logger.info('Get workflow latest version successfully! name: %s, version: %s', workflow_name, version)
        workflow_version = 1
        if version is not None:
            workflow_version = int(version) + 1
    else:
        workflow_version = version

    if os.path.exists(configs):
        try:
            workflow_temp = gdpy.yml_utils.yaml_loader(configs)
            workflow_temp['workflow']['name'] = workflow_name
            workflow_temp['workflow']['version'] = workflow_version
            workflow_temp = gdpy.yml_utils.yaml_dumper(workflow_temp)
        except (AttributeError, KeyError):
            print('Invalid config file! Please check "workflow" elements in the config file')
            sys.exit(-1)
    else:
        print('{} file not exists!'.format(configs))
        sys.exit(-1)

    with open(configs + '_tmp.yml', 'w') as f:
        f.write(workflow_temp.decode('utf-8'))

    resp = gdpy_operation(workflow.create_workflow, workflow_name, workflow_version, action='create workflow')
    if resp is None:
        print('Please check the input "workflow name", "workflow version" or "workflow config file".')
        os._exit(-1)

    resp = gdpy_operation(workflow.put_workflow, configs + '_tmp.yml', action='put workflow')
    if resp is None:
        print('Please check the input "workflow name", "workflow version" or "workflow config file".')
        os._exit(-1)

    os.remove(configs + '_tmp.yml')


def create_workflow(args):
    """
    创建工作流

    Args:
        args: 命令行解析的参数项

        args.name: 工作流名称
        args.configs: 工作流配置文件
        args.version: 工作流版本（不填默认为1，后面版本自动加1）
    """
    workflow_name = args.name
    configs = args.configs
    version = args.version

    _create_workflow(workflow_name, configs, version)


def delete_workflow(args):
    """
    删除工作流

    Args:
        args: 命令行解析的参数项

        args.name: 工作流名称
        args.version: 工作流版本（不填默认为最新版本）
    """
    endpoint, account_name, user_name, gd_auth = get_configuration()

    workflow_name = args.name

    if args.version is None:
        workflow_version = get_version('workflow', workflow_name, account_name, PROJECTNAME)
        if workflow_version is None:
            print('Please check the input "workflow name" or "resource account" (if authoried by others).')
            os._exit(1)
    else:
        workflow_version = args.version

    workflow = gdpy.Workflows(gd_auth, endpoint, account_name, PROJECTNAME)
    try:
        resp = workflow.delete_workflow(workflow_name, workflow_version)
        _logger.info('Deleting workflow successfully! name: {}, version: {}.'.format(workflow_name, workflow_version))
        print('Deleting workflow successfully! name: {}, version: {}.'.format(workflow_name, workflow_version),
              file=sys.stdout)
    except gdpy.exceptions.RequestError as e:
        _logger.warning(
            'Failed to delete the workflow! status: {}, error: {}'.format(e.status, e.error_message.decode('utf-8')))
        print('Failed to delete the workflow!\nstatus: {}\nerror: {}\n'.format(
            e.status, e.error_message.decode('utf-8')), file=sys.stderr)
        print('NetWork Connection Error, please check your network and retry.', file=sys.stderr)
    except gdpy.exceptions.ServerError as e:
        _logger.warning('Failed to delete the workflow! status: {}, error: {}, 错误: {}'.format(
            e.status, e.error_message.decode('utf-8'), e.error_message_chs.decode('utf-8')))
        print('Failed to delete the workflow!\nstatus: {}\nerror: {}\n错误: {}'.format(
            e.status, e.error_message.decode('utf-8'), e.error_message_chs.decode('utf-8')), file=sys.stderr)
        if e.status // 100 == 5:
            print('Please retry, if failed again, contact with the staff of GeneDock.', file=sys.stderr)
        elif e.status // 100 == 4:
            print('Please check the content of the input "workflow name" or "workflow version".', file=sys.stderr)
    except ValueError as e:
        _logger.warning('Failed to delete the workflow! error: {}'.format(e))
        print('Failed to delete the workflow!\nerror: {}'.format(e), file=sys.stderr)
        print('Please check the input "workflow name" or "workflow version".', file=sys.stderr)


def _get_workflow(workflow_name, version, output):
    """下载工作流配置文件
    :param workflow_name: 工作流名字
    :param version: 工作流版本
    :param output: 工作流信息输出文件
    :return:
    """
    endpoint, account_name, user_name, gd_auth = get_configuration()
    if version is None:
        workflow_version = get_version('workflow', workflow_name, account_name, PROJECTNAME)
        if workflow_version is None:
            print('Please check the input "workflow name" or "resource account" (if authoried by others).')
            os._exit(1)
    else:
        workflow_version = version

    workflow = gdpy.Workflows(gd_auth, endpoint, account_name, PROJECTNAME)
    resp = gdpy_operation(workflow.get_workflow, workflow_name, workflow_version, action='get workflow')
    if resp is None:
        print('Please check the input "workflow name" or "workflow version".')
        os._exit(-1)

    workflow_config_dic = gdpy.utils.json_loader(resp.response.text)
    workflow_config_dic['workflow'] = workflow_config_dic['workflows'][0]
    del workflow_config_dic['workflows']
    workflow_config_dic['workflow']['nodelist'] = workflow_config_dic['workflow']['configs']['nodelist']
    del workflow_config_dic['workflow']['configs']
    workflow_config_dic['workflow']['name'] = workflow_name
    workflow_config = gdpy.yml_utils.yaml_dumper(workflow_config_dic).decode('utf-8')

    if output:
        with open(output, 'w') as f:
            f.write(workflow_config)
        _logger.info('Get workflow successfully! name: {}, version: {}. The output was saved to the file "{}"!'.format(
            workflow_name, workflow_version, output))
        print('Get workflow successfully! The output was saved to the file "{}"!'.format(output))
    else:
        _logger.info('Get workflow successfully! name: {}, version: {}.'.format(workflow_name, workflow_version))
        print(workflow_config)
    return workflow_config_dic['workflow']['nodelist'], account_name


def get_workflow(args):
    """
    下载工作流配置文件

    Args：
        args: 命令行解析的参数项

        args.name: 工作流名称
        args.version: 工作流版本（不填默认为最新版本）
        args.output: 配置文件输出路径（不填默认输出到屏幕）
    """
    workflow_name = args.name
    version = args.version
    output = args.output
    _get_workflow(workflow_name, version, output)


def _get_workflow_param(workflow_name, account, output, version):
    """下载工作流参数配置模板
    :param workflow_name: 工作流名字
    :param account: 账户名
    :param output: 工作流参数的输出文件
    :param version: 工作流版本
    :return:
    """
    endpoint, account_name, user_name, gd_auth = get_configuration()
    if account:
        workflow_owner = account
    else:
        workflow_owner = account_name

    if version:
        workflow_version = version
    else:
        workflow_version = get_version('workflow', workflow_name, workflow_owner, PROJECTNAME)
        if workflow_version is None:
            print('Please check the input "workflow name" or "resource account" (if authoried by others).',
                  file=sys.stderr)
            os._exit(1)

    workflow = gdpy.Workflows(gd_auth, endpoint, workflow_owner, PROJECTNAME)
    resp = gdpy_operation(workflow.get_exc_workflow, workflow_name, workflow_version, action='get workflow parameters')
    if resp is None:
        print(
            'Please check the input "workflow name", "workflow version" or "resource account" '
            '(if authoried by others).', file=sys.stderr)
        os._exit(-1)

    workflow_param = gdpy.yml_utils.yaml_dumper(resp.parameter)

    if output:
        with open(output, 'w') as f:
            f.write(workflow_param.decode('utf-8'))
        _logger.info(
            'Get workflow parameters successfully! name: %s, version: %s. The output was saved to the file %s!',
            workflow_name, workflow_version, output)
        print('Get workflow parameters successfully! The output was saved to the file "{}"!'.format(output))
    else:
        _logger.info(
            'Get workflow parameters successfully! name: %s, version: %s.', workflow_name, workflow_version)
        print(workflow_param.decode('utf-8'))


def get_workflow_param(args):
    """
    下载工作流参数配置模板

    Args:
        args: 命令行解析的参数项

        args.name: 工作流名称
        args.account: 工作流账号归属（不填默认为当前账号，如需获取公共资源，则为public）
        args.output: 配置文件输出路径（不填默认输出到屏幕）
        args.version: 工作流版本（不填默认以最新版本运行）
    """
    workflow_name = args.name
    account = args.account
    output = args.output
    version = args.version
    _get_workflow_param(workflow_name, account, output, version)


def list_workflow(args):
    """
    列出自己创建的工作流和被授权的工作流

    Args：
        args: 命令行解析的参数项

        args.account: 工作流所属的资源账号，不加该参数项时，输出所有有权限的工作流
    """
    endpoint, account_name, user_name, gd_auth = get_configuration()

    if args.account is None:
        workflow_res_accounts = [account_name]
        try:
            resp = authpolicy.list_user_authorized_policy(endpoint, account_name, user_name, gd_auth)
            authorized_info = gdpy.utils.json_loader(resp.response.text)
            workflow_res_accounts.extend(authpolicy.get_workflow_authorizing_accounts(authorized_info))
            workflow_res_accounts = set(workflow_res_accounts)
            _logger.info('Listing user authorized policy successfully!')
        except gdpy.exceptions.RequestError as e:
            _logger.warning('Failed to list user authorized policy! '
                            'status: {}, error: {}'.format(e.status, e.error_message.decode('utf-8')))
            print('Failed to list user authorized policy!\nstatus: {}\nerror: {}\n'.format(
                e.status, e.error_message.decode('utf-8')), file=sys.stderr)
            print('NetWork Connection Error, please check your network and retry.', file=sys.stderr)
            sys.exit(-1)
        except gdpy.exceptions.ServerError as e:
            _logger.warning('Failed to list user authorized policy! status: {}, error: {}, 错误: {}'.format(
                e.status, e.error_message.decode('utf-8'), e.error_message_chs.decode('utf-8')))
            print('Failed to list user authorized policy!\nstatus: {}\nerror: {}\n错误: {}'.format(
                e.status, e.error_message.decode('utf-8'), e.error_message_chs.decode('utf-8')), file=sys.stderr)
            if e.status // 100 == 5:
                print('Please retry, if failed again, contact with the staff of GeneDock.', file=sys.stderr)
            elif e.status // 100 == 4:
                print('Please check the configuration info.', file=sys.stderr)
            sys.exit(-1)
    else:
        workflow_res_accounts = [args.account]

    workflow_template = []
    for res_account_name in workflow_res_accounts:
        workflow = gdpy.Workflows(gd_auth, endpoint, res_account_name, PROJECTNAME)
        try:
            resp = workflow.list_exc_workflows()
            for item in resp.workflows:
                for workflow_item in item:
                    workflow_item['workflow_account'] = res_account_name
                workflow_template.append(item)
            _logger.info('Listing workflow successfully! res_account: {}.'.format(res_account_name))
        except gdpy.exceptions.RequestError as e:
            _logger.warning(
                'Failed to list the workflow! status: {}, error: {}'.format(e.status, e.error_message.decode('utf-8')))
            print('Failed to list the workflow!\nstatus: {}\nerror: {}\n'.format(
                e.status, e.error_message.decode('utf-8')), file=sys.stderr)
            print('NetWork Connection Error, please check your network and retry.', file=sys.stderr)
        except gdpy.exceptions.ServerError as e:
            _logger.warning('Failed to list the workflow! status: {}, error: {}, 错误: {}'.format(
                e.status, e.error_message.decode('utf-8'), e.error_message_chs.decode('utf-8')))
            if e.status // 100 == 5:
                print('Please retry, if failed again, contact with the staff of GeneDock.', file=sys.stderr)
            elif e.status // 100 == 4:
                continue

    if workflow_template:
        table = json2table(gdpy.utils.json_dumper({'workflows': workflow_template}), 'workflows',
                           ['workflow_name', 'workflow_version', 'workflow_account', 'workflow_id', 'created_time',
                            'modified_time'], None)
        print(table, file=sys.stdout)
    else:
        print('Failed to list the workflow!')
        print('Please check the input "resource account name".')


def _set_workflow_param(workflow_name, configs, version):
    """预设工作流运行配置文件
    :param workflow_name: 工作流名称
    :param configs: 工作流运行配置文件路径
    :param version: 工作流版本
    :return:
    """
    endpoint, account_name, user_name, gd_auth = get_configuration()

    if os.path.exists(configs):
        workflow_temp = gdpy.yml_utils.yaml_loader(configs)
        try:
            conditions = workflow_temp['Conditions']
            inputs = workflow_temp['Inputs']
            outputs = workflow_temp['Outputs']
            parameters = workflow_temp['Parameters']
        except (AttributeError, KeyError):
            print(
                'Invalid config file! Please check "Conditions", "Inputs", "Outputs", '
                '"Parameters" elements in the config file',
                file=sys.stderr)
            sys.exit(-1)
    else:
        print('{} file not exists!'.format(configs))
        sys.exit(-1)

    workflow = gdpy.Workflows(gd_auth, endpoint, account_name, PROJECTNAME)
    resp = gdpy_operation(workflow.set_workflow_param, configs, workflow_name, version,
                          action='set workflow parameters')
    if resp is None:
        print('Please check "workflow name", "workflow version" or the content of the input "config file".')
        os._exit(-1)


def set_workflow_param(args):
    """
    预设工作流运行配置文件

    Args：
        args: 命令行解析的参数项

        args.name: 工作流名称
        args.configs: 工作流运行配置文件（即可执行工作流的配置文件）
        args.version: 工作流版本（不填默认为最新版本）
    """
    workflow_name = args.name
    configs = args.configs
    version = args.version
    _set_workflow_param(workflow_name, configs, version)


def update_workflow(args):
    """
    更新工作流配置文件

    Args：
        args: 命令行解析的参数项

        args.name: 工作流名称
        args.configs: 工作流配置文件
        args.version: 工作流版本（不填默认为最新版本）
    """
    endpoint, account_name, user_name, gd_auth = get_configuration()

    workflow_name = args.name

    if args.version is None:
        workflow_version = get_version('workflow', workflow_name, account_name, PROJECTNAME)
        if workflow_version is None:
            print('Please check the input "workflow name" or "resource account" (if authoried by others).')
            os._exit(1)
    else:
        workflow_version = args.version

    if os.path.exists(args.configs):
        try:
            workflow_temp = gdpy.yml_utils.yaml_loader(args.configs)
            if workflow_name != workflow_temp.get('workflow').get('name'):
                print('The input workflow name is not consistent with the name in the input config file.'.format(
                    workflow_name), file=sys.stderr)
                print('Please check the input "workflow name" or the "name" in the input config file', file=sys.stderr)
                sys.exit(-1)
            if workflow_version != workflow_temp.get('workflow').get('version'):
                print(
                    'The input workflow version (default: latest version) is not consistent with the version '
                    'in the input config file.',
                    file=sys.stderr)
                print('Please check the input "workflow version" or the "version" in the input config file!',
                      file=sys.stderr)
                sys.exit(-1)
        except (AttributeError, KeyError):
            print('Invalid config file! Please check "workflow", "name", "version" elements in the config file',
                  file=sys.stderr)
            sys.exit(-1)
    else:
        print('{} file not exists!'.format(args.configs), file=sys.stderr)
        sys.exit(-1)

    workflow = gdpy.Workflows(gd_auth, endpoint, account_name, PROJECTNAME)
    try:
        resp = workflow.put_workflow(args.configs)
        _logger.info('Updating workflow successfully! name: {}, version: {}.'.format(workflow_name, workflow_version))
        print('Updating workflow successfully! name: {}, version: {}.'.format(workflow_name, workflow_version),
              file=sys.stdout)
    except gdpy.exceptions.RequestError as e:
        _logger.warning(
            'Failed to update the workflow! status: {}, error: {}'.format(e.status, e.error_message.decode('utf-8')))
        print('Failed to update the workflow!\nstatus: {}\nerror: {}\n'.format(
            e.status, e.error_message.decode('utf-8')), file=sys.stderr)
        print('NetWork Connection Error, please check your network and retry.', file=sys.stderr)
    except gdpy.exceptions.ServerError as e:
        _logger.warning('Failed to update the workflow! status: {}, error: {}, 错误: {}'.format(
            e.status, e.error_message.decode('utf-8'), e.error_message_chs.decode('utf-8')))
        print('Failed to update the workflow!\nstatus: {}\nerror: {}\n错误: {}'.format(
            e.status, e.error_message.decode('utf-8'), e.error_message_chs.decode('utf-8')), file=sys.stderr)
        if e.status // 100 == 5:
            print('Please retry, if failed again, contact with the staff of GeneDock.', file=sys.stderr)
        elif e.status // 100 == 4:
            print(
                'Please check the content of the input "config file" or use "gwc workflow get" command to '
                'obtain the workflow original configuration file and remodify it',
                file=sys.stderr)
    except ValueError as e:
        _logger.warning('Failed to update the workflow! error: {}'.format(e))
        print('Failed to update the workflow!\nerror: {}'.format(e), file=sys.stderr)
        print('Please check the input "workflow name" or "workflow version".', file=sys.stderr)


def push_all_conf(args):
    """推送工作流配置文件, 工作流参数配置模板, 工具配置文件
    :param args:
                args.dir: 工作流配置的存放目录
    """
    if not os.path.exists(args.dir):
        print("The config file folder is not found!")
        os._exit(1)
    else:
        args.dir = re.sub('/$', '', args.dir)

    # configfiles check
    print("Step 1: Start to check workflow configuration.")
    if not os.path.exists(args.dir + "/Workflow") or not os.path.exists(args.dir + "/APP"):
        print("Can not find subdirectory 'Workflow' or 'APP'!")
        os._exit(1)
    elif len(os.listdir(args.dir + "/Workflow")) == 0:
        print("The workflow yaml configuration file is not specified!")
        os._exit(1)
    else:
        print("Check config file successfully!")

    # push apps
    '''
    首先上传APP，返回新的app_id后替换workflow配置文件中原来的app_id
    除了inputs/outputs/parameter内的项可以用作检查该APP在nodelist中的位置，没有其余可以作为唯一标识的内容
    一些app的inputs/outputs/parameter项相同，也不能当做可靠标识，暂时先用文件名来确定位置
    '''
    app_id_list = []
    print("\nStep 2: Start to push apps")

    for item in os.listdir(args.dir + "/APP"):
        tool_path = os.path.join(args.dir+"/APP/"+item)
        with open(tool_path, 'r') as f:
            app_info = yaml.load(f)
            print("\nStart to push apps: {} (verison: {})".format(app_info['app']['name'],
                                                                  app_info['app']['version']))
            # 上传APP前先确定该APP是否存在，若存在，获取其app id，若不存在，则创建新的APP并获取其app id
            tool_id = _get_tool(app_info['app']['name'], app_info['app']['version'], None, isreturnid=True)

            if tool_id:
                app_id_list.append((re.sub('_app.yml', '', item), tool_id))
                print("The app: {} (version: {}) already exists!".format(app_info['app']['name'],
                                                                         app_info['app']['version']))
            else:
                _create_tool(app_info['app']['name'], tool_path, app_info['app']['version'])
                tool_id = _get_tool(app_info['app']['name'], app_info['app']['version'], None, isreturnid=True)
                app_id_list.append((re.sub('_app.yml', '', item), tool_id))
                print("Push app: {} (verision: {}) successfully!".format(app_info['app']['name'],
                                                                             app_info['app']['version']))
        f.close()

    # replace app_ids and push workflow
    new_workflow_path = "{}/Workflow/{}_new_workflow.yml".format(args.dir, args.dir)
    old_workflow_path = "{}/Workflow/{}_workflow.yml".format(args.dir, args.dir)
    with open(old_workflow_path, 'r') as old_f, open(new_workflow_path, 'w') as new_f:
        workflow_template = old_f.read()
        for old_app_id, new_app_id in app_id_list:
            workflow_template = re.sub(old_app_id, new_app_id, workflow_template)
        new_f.write(workflow_template)
    old_f.close()
    new_f.close()

    print("\nStep 3: Start to push Workflow")
    with open(new_workflow_path, 'r') as f:
        workflow_info = yaml.load(f)
        _create_workflow(workflow_info['workflow']["name"], new_workflow_path,
                         workflow_info['workflow']["version"])
    print("Push workflow successfully!")

    # set workflow param
    print("\nStep 4: Start to set default parameters")
    workflow_para_path = '{}/Parameters/{}_parameter.yml'.format(args.dir, args.dir)
    _set_workflow_param(workflow_info['workflow']["name"], workflow_para_path,
                        workflow_info['workflow']["version"])
    print("Push workflow parameters successfully!")

    print("\nAll config pushed")


def pull_all_conf(args):
    """下载工作流配置文件，工作流参数配置模板，工具配置文件
    :param args:
                args.version: 工作流的版本
                args.name: 工作流的名字
    """
    endpoint, account_name, user_name, gd_auth = get_configuration()

    print("Step 1: Get Workflow Configure File:")
    # 获取 工作流版本号
    workflow_version = args.version
    if workflow_version is None:
        workflow_version = get_version('workflow', args.name, account_name, PROJECTNAME)
        if workflow_version is None:
            print('Please check the input "workflow name" or "resource account" (if authoried by others).')
            os._exit(1)
    # 生成工作流配置目录
    workflow_dir_name = "{0}_v{1}/Workflow".format(args.name, workflow_version)
    if not os.path.exists(workflow_dir_name):
        os.makedirs(workflow_dir_name)
    dir_name = "{}_v{}".format(args.name, workflow_version)
    workflow_config_path = "{0}/{1}_workflow.yml".format(workflow_dir_name, dir_name)

    (nodelists, account_name) = _get_workflow(args.name, workflow_version, workflow_config_path)

    print("\nStep 2: Get APP Configure File:")
    app_dir_name = '{0}/APP'.format(dir_name)

    if not os.path.exists(app_dir_name):
        os.makedirs(app_dir_name)

    for node in nodelists:
        print("\nGet APP: {} Configure File:".format(node['app_id']))

        if node['name'] in SYSTERMTOOL:
            print("Permission denied to get app: {} ({}), "
                  "it's a SYSTEM APP... pass".format(node['name'], node['app_id']))
            continue

        tool_version = get_version('tool', node['name'], account_name,
                                   project_name=PROJECTNAME, tool_id=node['app_id'])
        if tool_version is None:
            print("Permission denied to get app: {} ({}), "
                  "it's a PUBLIC APP... pass".format(node['name'], node['app_id']))
            continue

        path = '{0}/APP/{1}_app.yml'.format(dir_name, node['app_id'])
        _get_tool(node['name'], tool_version, path)

    print("\nStep 3: Get Workflow Parameter File:")

    if not os.path.exists(dir_name + '/Parameters'):
        os.mkdir(dir_name + '/Parameters')
    param_file_path = dir_name + '/Parameters/' + dir_name + "_parameter.yml"

    _get_workflow_param(args.name, account_name, param_file_path, workflow_version)

    print("\nAll config pulled")


def json2table(response, list_tag, labels, index):
    """
    将requests请求响应元素以表格形式整齐输出

    Args：
        response: requests请求响应元素
        list_tag: 响应元素中要解析的josn对象
        labels: json对象中的要解析的元素列表
        index: 按索引对响应元素排序

    Returns:
        table: 以表格形式返回requests请求响应元素
    """
    table = PrettyTable(labels)

    if index is not None:
        response = sorted(gdpy.utils.json_loader(response)[list_tag], key=lambda x: x[labels[index]])
    else:
        response = gdpy.utils.json_loader(response)[list_tag]

    for items in response:
        if type(items) == list:
            for item in items:
                line = list(
                    map(lambda x: gdpy.yml_utils.yaml_dumper(item.get(x)).decode('utf-8').strip('\n...\n'), labels))
                table.add_row(line)
        else:
            line = list(map(lambda x: gdpy.yml_utils.yaml_dumper(items.get(x)).decode('utf-8').strip('\n...\n')
                            .strip("'"), labels))
            table.add_row(line)
    table.align = 'l'
    table.junction_char = " "
    table.horizontal_char = " "
    table.vertical_char = " "
    return table


def main():
    parser = argparse.ArgumentParser(
        description='GeneDock workflow client (gwc) for interacting with GeneDock platform.')
    subparser = parser.add_subparsers()

    # configuration
    parser_config = subparser.add_parser('config',
                                         description='Configuration GeneDock API server, access id, access key, '
                                                     'account name and user name.',
                                         help='')
    parser_config.add_argument('-e', '--endpoint', help='GeneDock API server')
    parser_config.add_argument('-i', '--id', help='Access ID')
    parser_config.add_argument('-k', '--key', help='Access Key')
    parser_config.add_argument('-a', '--account', help='Account Name')
    parser_config.add_argument('-u', '--user', default='admin', help='User Name, default [admin]')
    parser_config.add_argument('ls', nargs='?', help='Listing configuration')
    parser_config.set_defaults(func=setup_configuration)

    # job operations
    parser_job = subparser.add_parser('job', description='Job operations', help='')
    subparser_job = parser_job.add_subparsers()

    subparser_job_getcmd = subparser_job.add_parser('getcmd', help='Get the job command')
    subparser_job_getcmd.add_argument('-i', '--jobid', required=True, help='job id')
    subparser_job_getcmd.set_defaults(func=get_job_cmd)

    subparsers_job_getlog = subparser_job.add_parser('getlog', help='Get the log of a job')
    subparsers_job_getlog.add_argument('-j', '--jobid', required=True, help="Specify the job id")
    subparsers_job_getlog.add_argument('-o', '--output', help='output file path')
    subparsers_job_getlog.set_defaults(func=get_job_log)

    # task operation
    parser_task = subparser.add_parser('task', description='Task operations', help='')
    subparser_task = parser_task.add_subparsers()

    subparser_task_delete = subparser_task.add_parser('delete', help='Delete task')
    subparser_task_delete.add_argument('-i', '--taskid', required=True, help='task id')
    subparser_task_delete.set_defaults(func=delete_task)

    subparser_task_get = subparser_task.add_parser('get', help='get task')
    subparser_task_get.add_argument('-i', '--taskid', required=True, help='task id')
    subparser_task_get.set_defaults(func=get_task)

    subparser_task_list = subparser_task.add_parser('ls', help='list task')
    subparser_task_list.add_argument('-s', '--size', type=int, default=500, help='maximum entries returned')
    subparser_task_list.add_argument('-f', '--fromdate',
                                     help='start date time, format: Y-m-d, default: 7 days ago of todate')
    subparser_task_list.add_argument('-t', '--todate', help='end date time, format: Y-m-d, default: current time')
    subparser_task_list.add_argument('-ts', '--totimestamp', action='store_true', help='时间格式转化成时间戳')
    subparser_task_list.set_defaults(func=list_task)

    subparser_task_stop = subparser_task.add_parser('stop', help='Stop task')
    subparser_task_stop.add_argument('-i', '--taskid', required=True, help='task id')
    subparser_task_stop.set_defaults(func=stop_task)

    subparsers_task_getjobs = subparser_task.add_parser('getjobs', help="Get the job list of a task")
    subparsers_task_getjobs.add_argument('-i', '--taskid', required=True, help="Specify the task id")
    subparsers_task_getjobs.add_argument('-q', '--quiet', action='store_true', help="Only show jobs IDs")
    subparsers_task_getjobs.set_defaults(func=get_jobs_info)

    subparser_task_stop = subparser_task.add_parser('getjobslog', help='Get job logs')
    subparser_task_stop.add_argument('-i', '--taskid', required=True, help='task id')
    subparser_task_stop.set_defaults(func=get_jobs_log)

    # tool operation
    parser_tool = subparser.add_parser('tool', description='Tool operations', help='')
    subparser_tool = parser_tool.add_subparsers()

    subparser_tool_create = subparser_tool.add_parser('create', help='Create tool')
    subparser_tool_create.add_argument('-n', '--name', required=True, help='tool name')
    subparser_tool_create.add_argument('-c', '--configs', required=True, help='config file path')
    subparser_tool_create.add_argument('-v', '--version', type=int, help='tool version')
    subparser_tool_create.set_defaults(func=create_tool)

    subparser_tool_delete = subparser_tool.add_parser('delete', help='Delete tool')
    subparser_tool_delete.add_argument('-n', '--name', required=True, help='tool name')
    subparser_tool_delete.add_argument('-v', '--version', type=int, help='tool version')
    subparser_tool_delete.set_defaults(func=delete_tool)

    subparser_tool_get = subparser_tool.add_parser('get', help='Get tool')
    subparser_tool_get.add_argument('-n', '--name', required=True, help='tool name')
    subparser_tool_get.add_argument('-v', '--version', type=int, help='tool version')
    subparser_tool_get.add_argument('-o', '--output', help='output file path')
    subparser_tool_get.set_defaults(func=get_tool)

    subparser_tool_ls = subparser_tool.add_parser('ls', help='List tool')
    subparser_tool_ls.add_argument('-a', '--account', help='tool resource account')
    subparser_tool_ls.set_defaults(func=list_tool)

    subparser_tool_update = subparser_tool.add_parser('update', help='Update tool')
    subparser_tool_update.add_argument('-n', '--name', required=True, help='tool name')
    subparser_tool_update.add_argument('-c', '--configs', required=True, help='config file path')
    subparser_tool_update.add_argument('-v', '--version', type=int, help='tool version')
    subparser_tool_update.set_defaults(func=update_tool)

    # workflow operations
    parser_workflow = subparser.add_parser('workflow', description='Workflow operations', help='')
    subparser_workflow = parser_workflow.add_subparsers()

    subparser_workflow_run = subparser_workflow.add_parser('run', help='Run workflow')
    subparser_workflow_run.add_argument('-n', '--name', required=True, help='workflow name')
    subparser_workflow_run.add_argument('-p', '--parameters', required=True, help='workflow parameters file')
    subparser_workflow_run.add_argument('-v', '--version', type=int, help='workflow version')
    subparser_workflow_run.add_argument('-a', '--account', help='workflow resource account')
    subparser_workflow_run.add_argument('-t', '--task', help='task name')
    subparser_workflow_run.set_defaults(func=active_workflow)

    subparser_workflow_create = subparser_workflow.add_parser('create', help='Create workflow')
    subparser_workflow_create.add_argument('-n', '--name', required=True, help='workflow name')
    subparser_workflow_create.add_argument('-c', '--configs', required=True, help='config file path')
    subparser_workflow_create.add_argument('-v', '--version', type=int, help='workflow version')
    subparser_workflow_create.set_defaults(func=create_workflow)

    subparser_workflow_delete = subparser_workflow.add_parser('delete', help='Delete workflow')
    subparser_workflow_delete.add_argument('-n', '--name', required=True, help='workflow name')
    subparser_workflow_delete.add_argument('-v', '--version', type=int, help='workflow version')
    subparser_workflow_delete.set_defaults(func=delete_workflow)

    subparser_workflow_get = subparser_workflow.add_parser('get', help='Get workflow')
    subparser_workflow_get.add_argument('-n', '--name', required=True, help='workflow name')
    subparser_workflow_get.add_argument('-v', '--version', type=int, help='workflow version')
    subparser_workflow_get.add_argument('-o', '--output', help='output file path')
    subparser_workflow_get.set_defaults(func=get_workflow)

    subparser_workflow_getparam = subparser_workflow.add_parser('getparam', help='Get workflow param')
    subparser_workflow_getparam.add_argument('-n', '--name', required=True, help='workflow name')
    subparser_workflow_getparam.add_argument('-o', '--output', help='output file path')
    subparser_workflow_getparam.add_argument('-v', '--version', type=int, help='workflow version')
    subparser_workflow_getparam.add_argument('-a', '--account', help='workflow resource account')
    subparser_workflow_getparam.set_defaults(func=get_workflow_param)

    subparser_workflow_ls = subparser_workflow.add_parser('ls', help='List workflow')
    subparser_workflow_ls.add_argument('-a', '--account', help='workflow resource account')
    subparser_workflow_ls.set_defaults(func=list_workflow)

    subparser_workflow_setparam = subparser_workflow.add_parser('setparam', help='Set workflow param')
    subparser_workflow_setparam.add_argument('-n', '--name', required=True, help='workflow name')
    subparser_workflow_setparam.add_argument('-c', '--configs', required=True, help='workflow param config file path')
    subparser_workflow_setparam.add_argument('-v', '--version', required=True, type=int, help='workflow version')
    subparser_workflow_setparam.set_defaults(func=set_workflow_param)

    subparser_workflow_update = subparser_workflow.add_parser('update', help='Update workflow')
    subparser_workflow_update.add_argument('-n', '--name', required=True, help='workflow name')
    subparser_workflow_update.add_argument('-c', '--configs', required=True, help='config file path')
    subparser_workflow_update.add_argument('-v', '--version', type=int, help='workflow version')
    subparser_workflow_update.set_defaults(func=update_workflow)

    # push all workflow resources to another region
    parsers_push = subparser.add_parser('push', help='Push All Workflow Configuration to a region')
    parsers_push.add_argument('-d', '--dir', required=True, help="Specify the configuration file dictionary")
    parsers_push.set_defaults(func=push_all_conf)


    # pull all workflow resources to local
    parsers_pull = subparser.add_parser('pull',
                                             help='Pull All Workflow Configuration File into a Local Dictionary')
    parsers_pull.add_argument('-n', '--name', required=True, help="Specify the workflow name")
    parsers_pull.add_argument('-v', '--version', type=int, help="Specify the workflow version")
    parsers_pull.set_defaults(func=pull_all_conf)

    parser.add_argument('-v', '--version', action='version', version='%(prog)s {0}'.format(__version__))

    args = parser.parse_args()
    try:
        args.func(args)
    except AttributeError:
        parser.error('too few arguments')


if __name__ == '__main__':
    main()
