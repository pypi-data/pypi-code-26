#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import argparse
import os
import platform
import pydoc
import sys
import time

from prettytable import PrettyTable

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
ENDPOINT_DICT = {'beijing': 'cn-beijing-api.genedock.com', 'qingdao': 'cn-qingdao-api.genedock.com', 'shenzhen': 'cn-shenzhen-api.genedock.com'}
CurrentTime = time.strftime('_%Y_%m_%d_%H_%M_%S', time.localtime())
PROJECTNAME = 'default'

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
        print('Using: "gwc config" or "gwc config -e [endpoint] -i [access_id] -k [access_key] -a [account_name] -u [user_name]".', file=sys.stderr)
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
        print('Using: "gwc config" or "gwc config -e [endpoint] -i [access_id] -k [access_key] -a [account_name] -u [user_name]".', file=sys.stderr)
        sys.exit(-1)
    except ConfigParser.NoOptionError as e:
        _logger.warning('Can not find option: "{}" in section: "{}" in config file: "{}".'.format(e.option, e.section, CONFIGFILE))
        print('Please config your account information.', file=sys.stderr)
        print('Using: "gwc config" or "gwc config -e [endpoint] -i [access_id] -k [access_key] -a [account_name] -u [user_name]".', file=sys.stderr)
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

            switch_choice = input('Choose region of GeneDock [Optionals: Beijing | Shenzhen | Qingdao, Default is Beijing]:').lower()
            while switch_choice != '' and switch_choice not in ENDPOINT_DICT.keys():
                switch_choice = input('Choose region of GeneDock [Optionals: Beijing | Shenzhen | Qingdao, Default is Beijing]:').lower()
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

            switch_choice = input('Enter the Account name or use the latest login Account [{}]:'.format(latest_account_name))
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
                print('KeyboardInterrupt')
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
        print('Using: gwc config -e [endpoint] -i [access_id] -k [access_key] -a [account_name] -u [user_name]', file=sys.stderr)
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


def get_latest_version(operation, name, res_account, project_name=PROJECTNAME):
    """
    获取工具或工作流的最新版本号

    Args：
        operation: 'workflow'或'tool'
        name: 工作流名称或工具名称
        res_account: 指定从该账号下获取资源

    Returns:
        version: 工作流或工具最新版本号
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
                if operation_version > version:
                    version = operation_version
        _logger.info('Get {} latest version successfully! name: {}, version: {}, resource account: {}.'.format(operation, name, version, res_account))
        return int(version)
    except gdpy.exceptions.RequestError as e:
        _logger.warning('Get {} latest version failed! status: {}, error: {}'.format(operation, e.status, e.error_message.decode('utf-8')))
        print('Get {} latest version failed!\nstatus: {}\nerror: {}'.format(operation, e.status, e.error_message.decode('utf-8')), file=sys.stderr)
        print('NetWork Connection Error, please check your network and retry.', file=sys.stderr)
        sys.exit(-1)
    except gdpy.exceptions.ServerError as e:
        _logger.warning('Get {} latest version failed! status: {}, error: {}, 错误: {}'.format(
            operation, e.status, e.error_message.decode('utf-8'), e.error_message_chs.decode('utf-8')))
        print('Get {} latest version failed!\nstatus: {}\nerror: {}\n错误: {}'.format(
            operation, e.status, e.error_message.decode('utf-8'), e.error_message_chs.decode('utf-8')), file=sys.stderr)
        if e.status // 100 == 5:
            print('Please retry, if failed again, contact with the staff of GeneDock.')
        elif e.status // 100 == 4:
            print('Please check the input "{} name" or "resource account" (if authoried by others).'.format(operation))
        sys.exit(-1)
    except ValueError as e:
        _logger.warning('Get {} latest version failed! error: {}'.format(operation, e))
        print('Get {} latest version failed!\nerror: {}'.format(operation, e), file=sys.stderr)
        print('Please check the input "{} name".'.format(operation), file=sys.stderr)
        sys.exit(-1)


def get_jobs_info(args):
    """
    列出指定task下的job信息

    Args:
        args: 命令行解析的参数项

        args.taskid: 指定task id
    """
    endpoint, account_name, user_name, gd_auth = get_configuration()

    task = gdpy.Tasks(gd_auth, endpoint, account_name, PROJECTNAME)
    task_id = args.taskid

    try:
        resp = task.get_jobs(task_id)
        table = json2table(resp.response.text, "jobs", ["job_id", "app_name", "status", "startTime", "endTime"], 1)
        _logger.info('Get jobs info successfully! task_id: {}.'.format(task_id))
        print(table, file=sys.stdout)
    except gdpy.exceptions.RequestError as e:
        _logger.warning('Failed to get jobs info! status: {}, error: {}'.format(e.status, e.error_message.decode('utf-8')))
        print('Failed to get jobs info!\nstatus: {}\nerror: {}\n'.format(
            e.status, e.error_message.decode('utf-8')), file=sys.stderr)
        print('NetWork Connection Error, please check your network and retry.', file=sys.stderr)
    except gdpy.exceptions.ServerError as e:
        _logger.warning('Failed to get jobs info! status: {}, error: {}, 错误: {}'.format(
            e.status, e.error_message.decode('utf-8'), e.error_message_chs.decode('utf-8')))
        print('Failed to get jobs info!\nstatus: {}\nerror: {}\n错误: {}'.format(
            e.status, e.error_message.decode('utf-8'), e.error_message_chs.decode('utf-8')), file=sys.stderr)
        if e.status // 100 == 5:
            print('Please retry, if failed again, contact with the staf of GeneDock.', file=sys.stderr)
        elif e.status // 100 == 4:
            print('Please check the input "task_id".', file=sys.stderr)


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
        _logger.warning('Failed to get the job command! status: {}, error: {}'.format(e.status, e.error_message.decode('utf-8')))
        print('Failed to get the job command!\nstatus: {}\nerror: {}\n'.format(
            e.status, e.error_message.decode('utf-8')), file=sys.stderr)
        print('NetWork Connection Error, please check your network and retry.', file=sys.stderr)
    except gdpy.exceptions.ServerError as e:
        _logger.warning('Failed to get the job command! status: {}, error: {}, 错误: {}'.format(
            e.status, e.error_message.decode('utf-8'), e.error_message_chs.decode('utf-8')))
        print('Failed to get the job command!\nstatus: {}\nerror: {}\n错误: {}'.format(
            e.status, e.error_message.decode('utf-8'), e.error_message_chs.decode('utf-8')), file=sys.stderr)
        if e.status // 100 == 5:
            print('Please retry, if failed again, contact with the staf of GeneDock.', file=sys.stderr)
        elif e.status // 100 == 4:
            print('Please check the input "job id" or whether you have permission to get the tool\'s cmd.', file=sys.stderr)


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
        _logger.warning('Failed to delete the task! status: {}, error: {}'.format(e.status, e.error_message.decode('utf-8')))
        print('Failed to delete the task!\nstatus: {}\nerror: {}\n'.format(
            e.status, e.error_message.decode('utf-8')), file=sys.stderr)
        print('NetWork Connection Error, please check your network and retry.', file=sys.stderr)
    except gdpy.exceptions.ServerError as e:
        _logger.warning('Failed to delete the task! status: {}, error: {}, 错误: {}'.format(
            e.status, e.error_message.decode('utf-8'), e.error_message_chs.decode('utf-8')))
        print('Failed to delete the task!\nstatus: {}\nerror: {}\n错误: {}'.format(
            e.status, e.error_message.decode('utf-8'), e.error_message_chs.decode('utf-8')), file=sys.stderr)
        if e.status // 100 == 5:
            print('Please retry, if failed again, contact with the staf of GeneDock.', file=sys.stderr)
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
        _logger.warning('Failed to get the task! status: {}, error: {}'.format(e.status, e.error_message.decode('utf-8')))
        print('Failed to get the task!\nstatus: {}\nerror: {}\n'.format(
            e.status, e.error_message.decode('utf-8')), file=sys.stderr)
        print('NetWork Connection Error, please check your network and retry.', file=sys.stderr)
    except gdpy.exceptions.ServerError as e:
        _logger.warning('Failed to get the task! status: {}, error: {}, 错误: {}'.format(
            e.status, e.error_message.decode('utf-8'), e.error_message_chs.decode('utf-8')))
        print('Failed to get the task!\nstatus: {}\nerror: {}\n错误: {}'.format(
            e.status, e.error_message.decode('utf-8'), e.error_message_chs.decode('utf-8')), file=sys.stderr)
        if e.status // 100 == 5:
            print('Please retry, if failed again, contact with the staf of GeneDock.', file=sys.stderr)
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
        table = json2table(resp.response.text, 'task_list', ['task_id', 'task_name', 'status', 'process', 'startTime', 'endTime', 'workflow_name', 'workflow_version'], None)
        _logger.info('Listing task successfully!')
        if platform.system() == 'Windows':
            print('Total tasks: {}, Count tasks: {}\n{}'.format(resp.total, len(resp.task_list), table))
        else:
            pydoc.pipepager('Total tasks: {}, Count tasks: {}\n{}'.format(resp.total, len(resp.task_list), str(table)), cmd='less -M -S')
    except gdpy.exceptions.RequestError as e:
        _logger.warning('Failed to list the task! status: {}, error: {}'.format(e.status, e.error_message.decode('utf-8')))
        print('Failed to list the task!\nstatus: {}\nerror: {}\n'.format(
            e.status, e.error_message.decode('utf-8')), file=sys.stderr)
        print('NetWork Connection Error, please check your network and retry.', file=sys.stderr)
    except gdpy.exceptions.ServerError as e:
        _logger.warning('Failed to list the task! status: {}, error: {}, 错误: {}'.format(
            e.status, e.error_message.decode('utf-8'), e.error_message_chs.decode('utf-8')))
        print('Failed to list the task!\nstatus: {}\nerror: {}\n错误: {}'.format(
            e.status, e.error_message.decode('utf-8'), e.error_message_chs.decode('utf-8')), file=sys.stderr)
        if e.status // 100 == 5:
            print('Please retry, if failed again, contact with the staf of GeneDock.', file=sys.stderr)
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
        _logger.warning('Failed to stop the task! status: {}, error: {}'.format(e.status, e.error_message.decode('utf-8')))
        print('Failed to stop the task!\nstatus: {}\nerror: {}\n'.format(
            e.status, e.error_message.decode('utf-8')), file=sys.stderr)
        print('NetWork Connection Error, please check your network and retry.', file=sys.stderr)
    except gdpy.exceptions.ServerError as e:
        _logger.warning('Failed to stop the task! status: {}, error: {}, 错误: {}'.format(
            e.status, e.error_message.decode('utf-8'), e.error_message_chs.decode('utf-8')))
        print('Failed to stop the task!\nstatus: {}\nerror: {}\n错误: {}'.format(
            e.status, e.error_message.decode('utf-8'), e.error_message_chs.decode('utf-8')), file=sys.stderr)
        if e.status // 100 == 5:
            print('Please retry, if failed again, contact with the staf of GeneDock.', file=sys.stderr)
        elif e.status // 100 == 4:
            print('Please check the input "task id".', file=sys.stderr)


def create_tool(args):
    """
    创建工具

    Args:
        args: 命令行解析的参数项

        args.name: 工具名称
        args.configs: 工具配置文件
        args.version: 工具版本（不填默认为1，后面版本自动加1）
    """
    endpoint, account_name, user_name, gd_auth = get_configuration()

    tool = gdpy.Tools(gd_auth, endpoint, account_name, PROJECTNAME)

    tool_name = args.name

    if args.version is None:
        try:
            version = 1
            resp = tool.get_tool(tool_name)
            for item in gdpy.utils.json_loader(resp.response.text).get('tools'):
                tool_version = item.get('configs').get('version')
                if tool_version > version:
                    version = tool_version
            _logger.info('Get tool latest version successfully! name: {}, version: {}'.format(tool_name, version))
            tool_version = int(version) + 1
        except gdpy.exceptions.ServerError as e:
            if e.status == 404:
                tool_version = 1
            else:
                _logger.warning('Get tool latest version failed! status: {}, error: {}, 错误: {}'.format(
                    e.status, e.error_message.decode('utf-8'), e.error_message_chs.decode('utf-8')))
                print('Get tool latest version failed!\nstatus: {}\nerror: {}\n错误: {}'.format(
                    e.status, e.error_message.decode('utf-8'), e.error_message_chs.decode('utf-8')), file=sys.stderr)
                if e.status // 100 == 5:
                    print('Please retry, if failed again, contact with the staff of GeneDock.')
                else:
                    print('Please check the input "tool name".')
                sys.exit(-1)
        except gdpy.exceptions.RequestError as e:
            _logger.warning('Get tool latest version failed! status: {}, error: {}'.format(e.status, e.error_message.decode('utf-8')))
            print('NetWork Connection Error, please check your network and retry.', file=sys.stderr)
            sys.exit(-1)
        except ValueError as e:
            _logger.warning('Get tool latest version failed! error: {}'.format(e))
            print('Get tool latest version failed!\nerror: {}'.format(e), file=sys.stderr)
            print('Please check the input "tool name".', file=sys.stderr)
            sys.exit(-1)
    else:
        tool_version = args.version

    if os.path.exists(args.configs):
        try:
            tool_temp = gdpy.yml_utils.yaml_loader(args.configs)
            tool_temp['app']['name'] = tool_name
            tool_temp['app']['version'] = tool_version
            tool_temp = gdpy.yml_utils.yaml_dumper(tool_temp)
        except (AttributeError, KeyError):
            print('Invalid config file! Please check "app" elements in the config file')
            sys.exit(-1)
    else:
        print('{} file not exists!'.format(args.configs))
        sys.exit(-1)

    with open(args.configs + '_tmp.yml', 'w') as f:
        f.write(tool_temp.decode('utf-8'))

    try:
        resp = tool.create_tool(tool_name, tool_version)
        resp = tool.put_tool(args.configs + '_tmp.yml')
        _logger.info('Create tool successfully! name: {}, version: {}.'.format(tool_name, tool_version))
        print('Create tool successfully! name: {}, version: {}.'.format(tool_name, tool_version), file=sys.stdout)
    except gdpy.exceptions.RequestError as e:
        _logger.warning('Failed to create tool! status: {}, error: {}'.format(e.status, e.error_message.decode('utf-8')))
        print('Failed to create tool!\nstatus: {}\nerror: {}\n'.format(
            e.status, e.error_message.decode('utf-8')), file=sys.stderr)
        print('NetWork Connection Error, please check your network and retry.', file=sys.stderr)
    except gdpy.exceptions.ServerError as e:
        _logger.warning('Failed to create tool! status: {}, error: {}, 错误: {}'.format(
            e.status, e.error_message.decode('utf-8'), e.error_message_chs.decode('utf-8')))
        print('Failed to create tool!\nstatus: {}\nerror: {}\n错误: {}'.format(
            e.status, e.error_message.decode('utf-8'), e.error_message_chs.decode('utf-8')), file=sys.stderr)
        if e.status // 100 == 5:
            print('Please retry, if failed again, contact with the staf of GeneDock.')
        elif e.status // 100 == 4:
            print('Please check the input "tool name", "tool version" or "tool config file".')
    except ValueError as e:
        _logger.warning('Failed to create the tool! error: {}'.format(e))
        print('Failed to create the tool!\nerror: {}'.format(e), file=sys.stderr)
        print('Please check the input "tool name" or "tool version".', file=sys.stderr)

    os.remove(args.configs + '_tmp.yml')


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
        tool_version = get_latest_version('tool', tool_name, account_name, PROJECTNAME)
    else:
        tool_version = args.version

    tool = gdpy.Tools(gd_auth, endpoint, account_name, PROJECTNAME)
    try:
        resp = tool.delete_tool(tool_name, tool_version)
        _logger.info('Deleting tool successfully! name: {}, version: {}.'.format(tool_name, tool_version))
        print('Deleting tool successfully! name: {}, version: {}.'.format(tool_name, tool_version), file=sys.stdout)
    except gdpy.exceptions.RequestError as e:
        _logger.warning('Failed to delete the tool! status: {}, error: {}'.format(e.status, e.error_message.decode('utf-8')))
        print('Failed to delete the tool!\nstatus: {}\nerror: {}\n'.format(
            e.status, e.error_message.decode('utf-8')), file=sys.stderr)
        print('NetWork Connection Error, please check your network and retry.', file=sys.stderr)
    except gdpy.exceptions.ServerError as e:
        _logger.warning('Failed to delete the tool! status: {}, error: {}, 错误: {}'.format(
            e.status, e.error_message.decode('utf-8'), e.error_message_chs.decode('utf-8')))
        print('Failed to delete the tool!\nstatus: {}\nerror: {}\n错误: {}'.format(
            e.status, e.error_message.decode('utf-8'), e.error_message_chs.decode('utf-8')), file=sys.stderr)
        if e.status // 100 == 5:
            print('Please retry, if failed again, contact with the staf of GeneDock.', file=sys.stderr)
        elif e.status // 100 == 4:
            print('Please check the content of the input "tool name" or "tool version".', file=sys.stderr)
    except ValueError as e:
        _logger.warning('Failed to delete the tool! error: {}'.format(e))
        print('Failed to delete the tool!\nerror: {}'.format(e), file=sys.stderr)
        print('Please check the input "tool name" or "tool version".', file=sys.stderr)


def get_tool(args):
    """
    下载工具配置文件

    Args：
        args: 命令行解析的参数项

        args.name: 工具名称
        args.version: 工具版本（不填默认为最新版本）
        args.output: 配置文件输出路径（不填默认输出到屏幕）
    """
    endpoint, account_name, user_name, gd_auth = get_configuration()

    tool_name = args.name

    if args.version is None:
        tool_version = get_latest_version('tool', tool_name, account_name, PROJECTNAME)
    else:
        tool_version = args.version

    tool = gdpy.Tools(gd_auth, endpoint, account_name, PROJECTNAME)
    try:
        resp = tool.get_tool(tool_name, tool_version)

        tool_config = gdpy.utils.json_loader(resp.response.text)
        tool_config['app'] = tool_config['tools'][0]['configs']
        del tool_config['tools']
        del tool_config['app']['_id']
        tool_config = gdpy.yml_utils.yaml_dumper(tool_config).decode('utf-8')

        if args.output:
            with open(args.output, 'w') as f:
                f.write(tool_config)
            _logger.info('Get tool successfully! name: {}, version: {}. The output was saved to the file "{}"!'.format(
                tool_name, tool_version, args.output))
            print('Get tool successfully! The output was saved to the file "{}"!'.format(args.output), file=sys.stderr)
        else:
            _logger.info('Get tool successfully! name: {}, version: {}.'.format(tool_name, tool_version))
            print(tool_config, file=sys.stdout)
    except gdpy.exceptions.RequestError as e:
        _logger.warning('Failed to get tool! status: {}, error: {}'.format(e.status, e.error_message.decode('utf-8')))
        print('Failed to get tool!\nstatus: {}\nerror: {}\n'.format(
            e.status, e.error_message.decode('utf-8')), file=sys.stderr)
        print('NetWork Connection Error, please check your network and retry.', file=sys.stderr)
    except gdpy.exceptions.ServerError as e:
        _logger.warning('Failed to get tool! status: {}, error: {}, 错误: {}'.format(
            e.status, e.error_message.decode('utf-8'), e.error_message_chs.decode('utf-8')))
        print('Failed to get tool!\nstatus: {}\nerror: {}\n错误: {}'.format(
            e.status, e.error_message.decode('utf-8'), e.error_message_chs.decode('utf-8')), file=sys.stderr)
        if e.status // 100 == 5:
            print('Please retry, if failed again, contact with the staf of GeneDock.')
        elif e.status // 100 == 4:
            print('Please check the input "tool name" or "tool version".')
    except ValueError as e:
        _logger.warning('Failed to get tool! error: {}'.format(e))
        print('Failed to get tool!\nerror: {}'.format(e), file=sys.stderr)
        print('Please check the input "tool name" or "tool version".', file=sys.stderr)


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
            _logger.warning('Failed to list user authorized policy! status: {}, error: {}'.format(e.status, e.error_message.decode('utf-8')))
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
                print('Please retry, if failed again, contact with the staf of GeneDock.', file=sys.stderr)
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
            _logger.warning('Failed to list the tool! status: {}, error: {}'.format(e.status, e.error_message.decode('utf-8')))
            print('Failed to list the tool!\nstatus: {}\nerror: {}\n'.format(
                e.status, e.error_message.decode('utf-8')), file=sys.stderr)
            print('NetWork Connection Error, please check your network and retry.', file=sys.stderr)
        except gdpy.exceptions.ServerError as e:
            _logger.warning('Failed to list the tool!\nstatus: {}, error: {}, 错误: {}'.format(
                e.status, e.error_message.decode('utf-8'), e.error_message_chs.decode('utf-8')))
            if e.status // 100 == 5:
                print('Please retry, if failed again, contact with the staf of GeneDock.', file=sys.stderr)
            else:
                continue

    if tool_template:
        table = json2table(gdpy.utils.json_dumper({'tools': tool_template}), 'tools', ['tool_name', 'tool_version', 'tool_account', 'tool_id', 'category', 'status'], None)
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
        tool_version = get_latest_version('tool', tool_name, account_name, PROJECTNAME)
    else:
        tool_version = args.version

    if os.path.exists(args.configs):
        try:
            tool_temp = gdpy.yml_utils.yaml_loader(args.configs)
            if tool_name != tool_temp.get('app').get('name'):
                print('The input tool name is not consistent with the name in the input config file.'.format(tool_name), file=sys.stderr)
                print('Please check the input "tool name" or the "name" in the input config file', file=sys.stderr)
                sys.exit(-1)
            if tool_version != tool_temp.get('app').get('version'):
                print('The input tool version (default: latest version) is not consistent with the version in the input config file.', file=sys.stderr)
                print('Please check the input "tool version" or the "version" in the input config file!', file=sys.stderr)
                sys.exit(-1)
        except (AttributeError, KeyError):
            print('Invalid config file! Please check "app", "name", "version" elements in the config file', file=sys.stderr)
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
        _logger.warning('Failed to update the tool! status: {}, error: {}'.format(e.status, e.error_message.decode('utf-8')))
        print('Failed to update the tool!\nstatus: {}\nerror: {}\n'.format(
            e.status, e.error_message.decode('utf-8')), file=sys.stderr)
        print('NetWork Connection Error, please check your network and retry.', file=sys.stderr)
    except gdpy.exceptions.ServerError as e:
        _logger.warning('Failed to update the tool! status: {}, error: {}, 错误: {}'.format(
            e.status, e.error_message.decode('utf-8'), e.error_message_chs.decode('utf-8')))
        print('Failed to update the tool!\nstatus: {}\nerror: {}\n错误: {}'.format(
            e.status, e.error_message.decode('utf-8'), e.error_message_chs.decode('utf-8')), file=sys.stderr)
        if e.status // 100 == 5:
            print('Please retry, if failed again, contact with the staf of GeneDock.', file=sys.stderr)
        elif e.status // 100 == 4:
            print('Please check the content of the input "config file" or use "gwc tool get" command to obtain the tool original configuration file and remodify it', file=sys.stderr)
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
        workflow_version = get_latest_version('workflow', workflow_name, workflow_owner, PROJECTNAME)

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
        print('Run the workflow successfully!\ntask_name: {}, task_id: {}'.format(resp.task_name, resp.task_id), file=sys.stdout)
    except gdpy.exceptions.RequestError as e:
        _logger.warning('Failed to active the workflow! status: {}, error: {}'.format(e.status, e.error_message.decode('utf-8')))
        print('Failed to active the workflow!\nstatus: {}\nerror: {}'.format(e.status, e.error_message.decode('utf-8')), file=sys.stderr)
        print('NetWork Connection Error, please check your network and retry.', file=sys.stderr)
    except gdpy.exceptions.ServerError as e:
        _logger.warning('Failed to active the workflow! status: {}, error: {}, 错误: {}'.format(
            e.status, e.error_message.decode('utf-8'), e.error_message_chs.decode('utf-8')))
        print('Failed to active the workflow!\nstatus: {}\nerror: {}\n错误: {}'.format(
            e.status, e.error_message.decode('utf-8'), e.error_message_chs.decode('utf-8')), file=sys.stderr)
        if e.status // 100 == 5:
            print('Please retry, if failed again, contact with the staff of GeneDock.')
        elif e.status // 100 == 4:
            print('Please check the input "workflow name", "workflow version", "the inputs data name in parameters file" or "resource account" (if authoried by others).')
    except ValueError as e:
        _logger.warning('Failed to active the workflow! error: {}'.format(e))
        print('Failed to active the workflow!\nerror: {}'.format(e), file=sys.stderr)
        print('Please check the input "workflow name" or "workflow version".', file=sys.stderr)

    os.remove(task_name + '_tmp.yml')


def create_workflow(args):
    """
    创建工作流

    Args:
        args: 命令行解析的参数项

        args.name: 工作流名称
        args.configs: 工作流配置文件
        args.version: 工作流版本（不填默认为1，后面版本自动加1）
    """
    endpoint, account_name, user_name, gd_auth = get_configuration()

    workflow = gdpy.Workflows(gd_auth, endpoint, account_name, PROJECTNAME)

    workflow_name = args.name

    if args.version is None:
        try:
            version = 1
            resp = workflow.get_workflow(workflow_name)
            for item in gdpy.utils.json_loader(resp.response.text).get('workflows'):
                workflow_version = item.get('version')
                if workflow_version > version:
                    version = workflow_version
            _logger.info('Get workflow latest version successfully! name: {}, version: {}'.format(workflow_name, version))
            workflow_version = int(version) + 1
        except gdpy.exceptions.ServerError as e:
            if e.status == 400:
                workflow_version = 1
            else:
                _logger.warning('Get workflow latest version failed! status: {}, error: {}, 错误: {}'.format(
                    e.status, e.error_message.decode('utf-8'), e.error_message_chs.decode('utf-8')))
                print('Get workflow latest version failed!\nstatus: {}\nerror: {}\n错误: {}'.format(
                    e.status, e.error_message.decode('utf-8'), e.error_message_chs.decode('utf-8')), file=sys.stderr)
                if e.status // 100 == 5:
                    print('Please retry, if failed again, contact with the staff of GeneDock.')
                else:
                    print('Please check the input "workflow name".')
                sys.exit(-1)
        except gdpy.exceptions.RequestError as e:
            _logger.warning('Get workflow latest version failed!\nstatus: {}, error: {}'.format(e.status, e.error_message.decode('utf-8')))
            print('Get workflow latest version failed!\nstatus: {}\nerror: {}'.format(e.status, e.error_message.decode('utf-8')), file=sys.stderr)
            print('NetWork Connection Error, please check your network and retry.', file=sys.stderr)
            sys.exit(-1)
        except ValueError as e:
            _logger.warning('Get workflow latest version failed!\nerror: {}'.format(e))
            print('Get workflow latest version failed!\nerror: {}'.format(e), file=sys.stderr)
            print('Please check the input "workflow name".', file=sys.stderr)
            sys.exit(-1)
    else:
        workflow_version = args.version

    if os.path.exists(args.configs):
        try:
            workflow_temp = gdpy.yml_utils.yaml_loader(args.configs)
            workflow_temp['workflow']['name'] = workflow_name
            workflow_temp['workflow']['version'] = workflow_version
            workflow_temp = gdpy.yml_utils.yaml_dumper(workflow_temp)
        except (AttributeError, KeyError):
            print('Invalid config file! Please check "workflow" elements in the config file', file=sys.stderr)
            sys.exit(-1)
    else:
        print('{} file not exists!'.format(args.configs), file=sys.stderr)
        sys.exit(-1)

    with open(args.configs + '_tmp.yml', 'w') as f:
        f.write(workflow_temp.decode('utf-8'))

    try:
        resp = workflow.create_workflow(workflow_name, workflow_version)
        resp = workflow.put_workflow(args.configs + '_tmp.yml')
        _logger.info('Create workflow successfully! name: {}, version: {}.'.format(workflow_name, workflow_version))
        print('Create workflow successfully! name: {}, version: {}.'.format(workflow_name, workflow_version), file=sys.stdout)
    except gdpy.exceptions.RequestError as e:
        _logger.warning('Failed to create workflow! status: {}, error: {}'.format(e.status, e.error_message.decode('utf-8')))
        print('Failed to create workflow!\nstatus: {}\nerror: {}\n'.format(
            e.status, e.error_message.decode('utf-8')), file=sys.stderr)
        print('NetWork Connection Error, please check your network and retry.', file=sys.stderr)
    except gdpy.exceptions.ServerError as e:
        _logger.warning('Failed to create workflow! status: {}, error: {}, 错误: {}'.format(
            e.status, e.error_message.decode('utf-8'), e.error_message_chs.decode('utf-8')))
        print('Failed to create workflow!\nstatus: {}\nerror: {}\n错误: {}'.format(
            e.status, e.error_message.decode('utf-8'), e.error_message_chs.decode('utf-8')), file=sys.stderr)
        if e.status // 100 == 5:
            print('Please retry, if failed again, contact with the staf of GeneDock.')
        elif e.status // 100 == 4:
            print('Please check the input "workflow name", "workflow version" or "workflow config file".')
    except ValueError as e:
        _logger.warning('Failed to create the workflow! error: {}'.format(e))
        print('Failed to create the workflow!\nerror: {}'.format(e), file=sys.stderr)
        print('Please check the input "workflow name" or "workflow version".', file=sys.stderr)

    os.remove(args.configs + '_tmp.yml')


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
        workflow_version = get_latest_version('workflow', workflow_name, account_name, PROJECTNAME)
    else:
        workflow_version = args.version

    workflow = gdpy.Workflows(gd_auth, endpoint, account_name, PROJECTNAME)
    try:
        resp = workflow.delete_workflow(workflow_name, workflow_version)
        _logger.info('Deleting workflow successfully! name: {}, version: {}.'.format(workflow_name, workflow_version))
        print('Deleting workflow successfully! name: {}, version: {}.'.format(workflow_name, workflow_version), file=sys.stdout)
    except gdpy.exceptions.RequestError as e:
        _logger.warning('Failed to delete the workflow! status: {}, error: {}'.format(e.status, e.error_message.decode('utf-8')))
        print('Failed to delete the workflow!\nstatus: {}\nerror: {}\n'.format(
            e.status, e.error_message.decode('utf-8')), file=sys.stderr)
        print('NetWork Connection Error, please check your network and retry.', file=sys.stderr)
    except gdpy.exceptions.ServerError as e:
        _logger.warning('Failed to delete the workflow! status: {}, error: {}, 错误: {}'.format(
            e.status, e.error_message.decode('utf-8'), e.error_message_chs.decode('utf-8')))
        print('Failed to delete the workflow!\nstatus: {}\nerror: {}\n错误: {}'.format(
            e.status, e.error_message.decode('utf-8'), e.error_message_chs.decode('utf-8')), file=sys.stderr)
        if e.status // 100 == 5:
            print('Please retry, if failed again, contact with the staf of GeneDock.', file=sys.stderr)
        elif e.status // 100 == 4:
            print('Please check the content of the input "workflow name" or "workflow version".', file=sys.stderr)
    except ValueError as e:
        _logger.warning('Failed to delete the workflow! error: {}'.format(e))
        print('Failed to delete the workflow!\nerror: {}'.format(e), file=sys.stderr)
        print('Please check the input "workflow name" or "workflow version".', file=sys.stderr)


def get_workflow(args):
    """
    下载工作流配置文件

    Args：
        args: 命令行解析的参数项

        args.name: 工作流名称
        args.version: 工作流版本（不填默认为最新版本）
        args.output: 配置文件输出路径（不填默认输出到屏幕）
    """
    endpoint, account_name, user_name, gd_auth = get_configuration()

    workflow_name = args.name

    if args.version is None:
        workflow_version = get_latest_version('workflow', workflow_name, account_name, PROJECTNAME)
    else:
        workflow_version = args.version

    workflow = gdpy.Workflows(gd_auth, endpoint, account_name, PROJECTNAME)
    try:
        resp = workflow.get_workflow(workflow_name, workflow_version)

        workflow_config = gdpy.utils.json_loader(resp.response.text)
        workflow_config['workflow'] = workflow_config['workflows'][0]
        del workflow_config['workflows']
        workflow_config['workflow']['nodelist'] = workflow_config['workflow']['configs']['nodelist']
        del workflow_config['workflow']['configs']
        workflow_config['workflow']['name'] = workflow_name
        workflow_config = gdpy.yml_utils.yaml_dumper(workflow_config).decode('utf-8')

        if args.output:
            with open(args.output, 'w') as f:
                f.write(workflow_config)
            _logger.info('Get workflow successfully! name: {}, version: {}. The output was saved to the file "{}"!'.format(
                workflow_name, workflow_version, args.output))
            print('Get workflow successfully! The output was saved to the file "{}"!'.format(args.output), file=sys.stderr)
        else:
            _logger.info('Get workflow successfully! name: {}, version: {}.'.format(workflow_name, workflow_version))
            print(workflow_config, file=sys.stdout)
    except gdpy.exceptions.RequestError as e:
        _logger.warning('Failed to get workflow! status: {}, error: {}'.format(e.status, e.error_message.decode('utf-8')))
        print('Failed to get workflow!\nstatus: {}\nerror: {}\n'.format(
            e.status, e.error_message.decode('utf-8')), file=sys.stderr)
        print('NetWork Connection Error, please check your network and retry.', file=sys.stderr)
    except gdpy.exceptions.ServerError as e:
        _logger.warning('Failed to get workflow! status: {}, error: {}, 错误: {}'.format(
            e.status, e.error_message.decode('utf-8'), e.error_message_chs.decode('utf-8')))
        print('Failed to get workflow!\nstatus: {}\nerror: {}\n错误: {}'.format(
            e.status, e.error_message.decode('utf-8'), e.error_message_chs.decode('utf-8')), file=sys.stderr)
        if e.status // 100 == 5:
            print('Please retry, if failed again, contact with the staf of GeneDock.')
        elif e.status // 100 == 4:
            print('Please check the input "workflow name" or "workflow version".')
    except ValueError as e:
        _logger.warning('Failed to get workflow! error: {}'.format(e))
        print('Failed to get workflow!\nerror: {}'.format(e), file=sys.stderr)
        print('Please check the input "workflow name" or "workflow version".', file=sys.stderr)


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
    endpoint, account_name, user_name, gd_auth = get_configuration()

    workflow_name = args.name

    if args.account:
        workflow_owner = args.account
    else:
        workflow_owner = account_name

    if args.version:
        workflow_version = args.version
    else:
        workflow_version = get_latest_version('workflow', workflow_name, workflow_owner, PROJECTNAME)

    workflow = gdpy.Workflows(gd_auth, endpoint, workflow_owner, PROJECTNAME)
    try:
        resp = workflow.get_exc_workflow(workflow_name, workflow_version)
        workflow_param = gdpy.yml_utils.yaml_dumper(resp.parameter)
        if args.output:
            with open(args.output, 'w') as f:
                f.write(workflow_param.decode('utf-8'))
            _logger.info('Get workflow parameters successfully! name: {}, version: {}. The output was saved to the file "{}"!'.format(
                workflow_name, workflow_version, args.output))
            print('Get workflow parameters successfully! The output was saved to the file "{}"!'.format(args.output), file=sys.stdout)
        else:
            _logger.info('Get workflow parameters successfully! name: {}, version: {}.'.format(workflow_name, workflow_version))
            print(workflow_param.decode('utf-8'), file=sys.stdout)
    except gdpy.exceptions.RequestError as e:
        _logger.warning('Failed to get the workflow parameters! status: {}, error: {}'.format(e.status, e.error_message.decode('utf-8')))
        print('Failed to get the workflow parameters!\nstatus: {}\nerror: {}\n'.format(
            e.status, e.error_message.decode('utf-8')), file=sys.stderr)
        print('NetWork Connection Error, please check your network and retry.', file=sys.stderr)
    except gdpy.exceptions.ServerError as e:
        _logger.warning('Failed to get the workflow parameters! status: {}, error: {}, 错误: {}'.format(
            e.status, e.error_message.decode('utf-8'), e.error_message_chs.decode('utf-8')))
        print('Failed to get the workflow parameters!\nstatus: {}\nerror: {}\n错误: {}'.format(
            e.status, e.error_message.decode('utf-8'), e.error_message_chs.decode('utf-8')), file=sys.stderr)
        if e.status // 100 == 5:
            print('Please retry, if failed again, contact with the staf of GeneDock.')
        elif e.status // 100 == 4:
            print('Please check the input "workflow name", "workflow version" or "resource account" (if authoried by others).')
    except ValueError as e:
        _logger.warning('Failed to get the workflow parameters! error: {}'.format(e))
        print('Failed to get the workflow parameters!\nerror: {}'.format(e), file=sys.stderr)
        print('Please check the input "workflow name" or "workflow version".', file=sys.stderr)


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
            _logger.warning('Failed to list user authorized policy! status: {}, error: {}'.format(e.status, e.error_message.decode('utf-8')))
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
                print('Please retry, if failed again, contact with the staf of GeneDock.', file=sys.stderr)
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
            _logger.warning('Failed to list the workflow! status: {}, error: {}'.format(e.status, e.error_message.decode('utf-8')))
            print('Failed to list the workflow!\nstatus: {}\nerror: {}\n'.format(
                e.status, e.error_message.decode('utf-8')), file=sys.stderr)
            print('NetWork Connection Error, please check your network and retry.', file=sys.stderr)
        except gdpy.exceptions.ServerError as e:
            _logger.warning('Failed to list the workflow! status: {}, error: {}, 错误: {}'.format(
                e.status, e.error_message.decode('utf-8'), e.error_message_chs.decode('utf-8')))
            if e.status // 100 == 5:
                print('Please retry, if failed again, contact with the staf of GeneDock.', file=sys.stderr)
            elif e.status // 100 == 4:
                continue

    if workflow_template:
        table = json2table(gdpy.utils.json_dumper({'workflows': workflow_template}), 'workflows', ['workflow_name', 'workflow_version', 'workflow_account', 'workflow_id', 'created_time', 'modified_time'], None)
        print(table, file=sys.stdout)
    else:
        print('Failed to list the workflow!')
        print('Please check the input "resource account name".')


def set_workflow_param(args):
    """
    预设工作流运行配置文件

    Args：
        args: 命令行解析的参数项

        args.name: 工作流名称
        args.configs: 工作流运行配置文件（即可执行工作流的配置文件）
        args.version: 工作流版本（不填默认为最新版本）
    """
    endpoint, account_name, user_name, gd_auth = get_configuration()

    workflow_name = args.name

    if args.version is None:
        workflow_version = get_latest_version('workflow', workflow_name, account_name, PROJECTNAME)
    else:
        workflow_version = args.version

    if os.path.exists(args.configs):
        workflow_temp = gdpy.yml_utils.yaml_loader(args.configs)
        try:
            conditions = workflow_temp['Conditions']
            inputs = workflow_temp['Inputs']
            outputs = workflow_temp['Outputs']
            parameters = workflow_temp['Parameters']
        except (AttributeError, KeyError):
            print('Invalid config file! Please check "Conditions", "Inputs", "Outputs", "Parameters" elements in the config file', file=sys.stderr)
            sys.exit(-1)
    else:
        print('{} file not exists!'.format(args.configs), file=sys.stderr)
        sys.exit(-1)

    workflow = gdpy.Workflows(gd_auth, endpoint, account_name, PROJECTNAME)
    try:
        resp = workflow.set_workflow_param(args.configs, workflow_name, workflow_version)
        _logger.info('Setting workflow parameters successfully! name: {}, version: {}.'.format(workflow_name, workflow_version))
        print('Setting workflow parameters successfully! name: {}, version: {}.'.format(workflow_name, workflow_version), file=sys.stdout)
    except gdpy.exceptions.RequestError as e:
        _logger.warning('Failed to set the workflow parameters! status: {}, error: {}'.format(e.status, e.error_message.decode('utf-8')))
        print('Failed to set the workflow parameters!\nstatus: {}\nerror: {}\n'.format(
            e.status, e.error_message.decode('utf-8')), file=sys.stderr)
        print('NetWork Connection Error, please check your network and retry.', file=sys.stderr)
    except gdpy.exceptions.ServerError as e:
        _logger.warning('Failed to set the workflow parameters! status: {}, error: {}, 错误: {}'.format(
            e.status, e.error_message.decode('utf-8'), e.error_message_chs.decode('utf-8')))
        print('Failed to set the workflow parameters!\nstatus: {}\nerror: {}\n错误: {}'.format(
            e.status, e.error_message.decode('utf-8'), e.error_message_chs.decode('utf-8')), file=sys.stderr)
        if e.status // 100 == 5:
            print('Please retry, if failed again, contact with the staf of GeneDock.', file=sys.stderr)
        elif e.status // 100 == 4:
            print('Please check "workflow name", "workflow version" or the content of the input "config file".', file=sys.stderr)
    except ValueError as e:
        _logger.warning('Failed to set the workflow parameters! error: {}'.format(e))
        print('Failed to set the workflow parameters!\nerror: {}'.format(e), file=sys.stderr)
        print('Please check the input "workflow name" or "workflow version".', file=sys.stderr)


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
        workflow_version = get_latest_version('workflow', workflow_name, account_name, PROJECTNAME)
    else:
        workflow_version = args.version

    if os.path.exists(args.configs):
        try:
            workflow_temp = gdpy.yml_utils.yaml_loader(args.configs)
            if workflow_name != workflow_temp.get('workflow').get('name'):
                print('The input workflow name is not consistent with the name in the input config file.'.format(workflow_name), file=sys.stderr)
                print('Please check the input "workflow name" or the "name" in the input config file', file=sys.stderr)
                sys.exit(-1)
            if workflow_version != workflow_temp.get('workflow').get('version'):
                print('The input workflow version (default: latest version) is not consistent with the version in the input config file.', file=sys.stderr)
                print('Please check the input "workflow version" or the "version" in the input config file!', file=sys.stderr)
                sys.exit(-1)
        except (AttributeError, KeyError):
            print('Invalid config file! Please check "workflow", "name", "version" elements in the config file', file=sys.stderr)
            sys.exit(-1)
    else:
        print('{} file not exists!'.format(args.configs), file=sys.stderr)
        sys.exit(-1)

    workflow = gdpy.Workflows(gd_auth, endpoint, account_name, PROJECTNAME)
    try:
        resp = workflow.put_workflow(args.configs)
        _logger.info('Updating workflow successfully! name: {}, version: {}.'.format(workflow_name, workflow_version))
        print('Updating workflow successfully! name: {}, version: {}.'.format(workflow_name, workflow_version), file=sys.stdout)
    except gdpy.exceptions.RequestError as e:
        _logger.warning('Failed to update the workflow! status: {}, error: {}'.format(e.status, e.error_message.decode('utf-8')))
        print('Failed to update the workflow!\nstatus: {}\nerror: {}\n'.format(
            e.status, e.error_message.decode('utf-8')), file=sys.stderr)
        print('NetWork Connection Error, please check your network and retry.', file=sys.stderr)
    except gdpy.exceptions.ServerError as e:
        _logger.warning('Failed to update the workflow! status: {}, error: {}, 错误: {}'.format(
            e.status, e.error_message.decode('utf-8'), e.error_message_chs.decode('utf-8')))
        print('Failed to update the workflow!\nstatus: {}\nerror: {}\n错误: {}'.format(
            e.status, e.error_message.decode('utf-8'), e.error_message_chs.decode('utf-8')), file=sys.stderr)
        if e.status // 100 == 5:
            print('Please retry, if failed again, contact with the staf of GeneDock.', file=sys.stderr)
        elif e.status // 100 == 4:
            print('Please check the content of the input "config file" or use "gwc workflow get" command to obtain the workflow original configuration file and remodify it', file=sys.stderr)
    except ValueError as e:
        _logger.warning('Failed to update the workflow! error: {}'.format(e))
        print('Failed to update the workflow!\nerror: {}'.format(e), file=sys.stderr)
        print('Please check the input "workflow name" or "workflow version".', file=sys.stderr)


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
                line = list(map(lambda x: gdpy.yml_utils.yaml_dumper(item.get(x)).decode('utf-8').strip('\n...\n'), labels))
                table.add_row(line)
        else:
            line = list(map(lambda x: gdpy.yml_utils.yaml_dumper(items.get(x)).decode('utf-8').strip('\n...\n'), labels))
            table.add_row(line)
    table.align = 'l'
    table.junction_char = " "
    table.horizontal_char = " "
    table.vertical_char = " "
    return table


def main():
    parser = argparse.ArgumentParser(description='GeneDock workflow client (gwc) for interacting with GeneDock platform.')
    subparser = parser.add_subparsers()

    # configuration
    parser_config = subparser.add_parser('config', description='Configuration GeneDock API server, access id, access key, account name and user name.', help='')
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

    subparser_job_ls = subparser_job.add_parser('ls', help='Get the job list of a task')
    subparser_job_ls.add_argument('-i', '--taskid', required=True, help='task id')
    subparser_job_ls.set_defaults(func=get_jobs_info)

    subparser_job_getcmd = subparser_job.add_parser('getcmd', help='Get the job command')
    subparser_job_getcmd.add_argument('-i', '--jobid', required=True, help='job id')
    subparser_job_getcmd.set_defaults(func=get_job_cmd)

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
    subparser_task_list.add_argument('-f', '--fromdate', help='start date time, format: Y-m-d, default: 7 days ago of todate')
    subparser_task_list.add_argument('-t', '--todate', help='end date time, format: Y-m-d, default: current time')
    subparser_task_list.set_defaults(func=list_task)

    subparser_task_stop = subparser_task.add_parser('stop', help='Stop task')
    subparser_task_stop.add_argument('-i', '--taskid', required=True, help='task id')
    subparser_task_stop.set_defaults(func=stop_task)

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
    subparser_workflow_setparam.add_argument('-v', '--version', type=int, help='workflow version')
    subparser_workflow_setparam.set_defaults(func=set_workflow_param)

    subparser_workflow_update = subparser_workflow.add_parser('update', help='Update workflow')
    subparser_workflow_update.add_argument('-n', '--name', required=True, help='workflow name')
    subparser_workflow_update.add_argument('-c', '--configs', required=True, help='config file path')
    subparser_workflow_update.add_argument('-v', '--version', type=int, help='workflow version')
    subparser_workflow_update.set_defaults(func=update_workflow)

    parser.add_argument('-v', '--version', action='version', version='%(prog)s {0}'.format(__version__))

    args = parser.parse_args()
    try:
        args.func(args)
    except AttributeError:
        parser.error('too few arguments')


if __name__ == '__main__':
    main()
