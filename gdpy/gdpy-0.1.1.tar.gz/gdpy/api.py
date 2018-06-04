# -*- coding:utf-8 -*-

import json
from . import defaults
from . import http
from . import yml_utils
from . import exceptions
from . import utils
from .compat import urlparse, to_unicode, to_string, to_json
from .models import *
import time


def _normalize_endpoint(endpoint):
    if not endpoint.startswith('http://') and not endpoint.startswith('https://'):
        return 'https://' + endpoint
    else:
        return endpoint


class _Base(object):
    def __init__(self, auth, endpoint, connect_timeout):
        self.session = http.Session()
        self.auth = auth
        self.endpoint = _normalize_endpoint(endpoint)
        self.timeout = defaults.get(connect_timeout, defaults.connect_timeout)

    def _do(self, method, res_account_name, project_name, target, **kwargs):
        target = to_string(target)
        make_url = _UrlMaker(self.endpoint, kwargs.pop('operation'))
        self.data = kwargs.pop('data', None)
        self.params = kwargs.pop('params', None)
        req = http.Request(method, self.auth, make_url(res_account_name, project_name, target, **kwargs), data=self.data, params=self.params)

        resp = self.session.do_request(req, timeout=self.timeout)
        if resp.status // 100 != 2:
            raise exceptions.make_exception(resp)

        return resp

    def _parse_result(self, resp, parse_func, klass):
        result = klass(resp)
        parse_func(result, resp.response.content)
        return result

    def _get_url(self, res_account_name, res_project_name, target, **kwargs):
        return self._make_url(res_account_name, res_project_name, target, **kwargs)


class _UrlMaker(object):

    def __init__(self, endpoint, operation):
        p = urlparse(endpoint)

        self.scheme = p.scheme
        self.netloc = p.netloc
        self.operation = operation

    def __call__(self, res_account_name, res_project_name, target, **kwargs):
        self.project_name = res_project_name
        self.account_name = res_account_name
        end_slash = kwargs.pop('end_slash', 1)
        if target:
            if not len(kwargs):
                url = '{0}://{1}/accounts/{2}/projects/{3}/{4}/{5}/'.format(self.scheme, self.netloc,
                                                                            self.account_name, self.project_name, self.operation, target)
                if end_slash==0:
                    return url[:-1]
                else:
                    return url
            else:
                params = list()
                for item in kwargs:
                    if kwargs.get(item):
                        params.append(item + '=' + str(kwargs.get(item)))
                parameters = '?' + '&'.join(params)
                return '{0}://{1}/accounts/{2}/projects/{3}/{4}/{5}/{6}'.format(self.scheme, self.netloc, self.account_name, self.project_name, self.operation, target, parameters)
        else:
            return '{0}://{1}/accounts/{2}/projects/{3}/{4}/'.format(self.scheme, self.netloc, self.account_name, self.project_name, self.operation)


class Tasks(_Base):
    """ 用于Tasks操作的类
    :param auth: 包含了用户认证信息的Auth对象
    :type auth: gdpy.GeneDockAuth

    :param str endpoint: 访问域名，如北京区域的域名为cn-beijing-api.genedock.com
    :param str res_account_name: 指定从该账号下获取资源(如需获取公共资源，则为public)
    :param str res_project_name: 指定从该项目下获取资源(默认为default)
    :raises: 如果获取或上传失败，则抛出来自服务端的异常; 还可能抛出其他异常
    tasks related operations
    usage::
        >>> import gdpy
        >>> auth = gdpy.GeneDockAuth('access_key_id', 'access_key_secret')
        >>> task = gdpy.Tasks(auth, 'https://cn-beijing-api.genedock.com', 'res_account_name', 'project_name')
    """
    def __init__(self, auth, endpoint, res_account_name, project_name='default', connect_timeout=None):
        super(Tasks, self).__init__(auth, endpoint, connect_timeout)
        self.res_account_name = res_account_name
        self.res_project_name = project_name

    def __do_task(self, method, id=None, **kwargs):
        return self._do(method, self.res_account_name, self.res_project_name, id, **kwargs)

    def get_task(self, id):
        """
        usage:
            >>> resp = task.get_task('task_id')
        """
        resp = self.__do_task('GET', id, operation='tasks')
        return GetTaskResult(resp)

    def list_tasks(self, **kwargs):
        """
        usage:
            >>> resp = task.list_tasks()
        """
        default_to = int(time.time())
        default_from = default_to - 60 * 60 * 24 * 7
        params = {'from': default_from, 'to': default_to}
        if 'params' in list(kwargs.keys()):
            resp = self.__do_task('GET', operation='tasks', **kwargs)
        else:
            resp = self.__do_task('GET', params=params, operation='tasks', **kwargs)
        return self._parse_result(resp, yml_utils.parse_list_tasks, ListTasksResult)

    def active_workflow(self, param_file, workflow_name, workflow_version, workflow_owner=None):
        """
        usage::
            >>> resp = task.active_workflow('workflow_param_file', 'workflow_name', 'workflow_version')
        """
        if not workflow_owner:
            workflow_owner = self.res_account_name
        if not is_object_name_valid(workflow_name):
            raise ValueError("Invalid workflow name! Expect a string started with alphabet and under 128 characters, but got {}!".format(str(workflow_name)))
        if not is_object_version_valid(workflow_version):
            raise ValueError("Invalid workflow version! Expect interger greater than 0, but got {}".format(str(workflow_version)))
        try:
            data = dict()
            data["parameters"] = yml_utils.yaml_loader(param_file)
            data["workflow_name"] = workflow_name
            data["workflow_version"] = int(workflow_version)
            data["workflow_owner"] = workflow_owner
            data["task_name"] = data["parameters"].get("name")
            resp = self.__do_task('POST', '', data=data, operation='tasks')
        except ValueError as e:
            raise e
        return ActiveWorkflowResult(resp)

    def delete_task(self, id):
        """
        usage:
            >>> resp = task.delete_task('task_id')
        """
        resp = self.__do_task('DELETE', id, operation='tasks')
        return DeleteTaskResult(resp)

    def stop_task(self, id):
        """
        usage:
            >>> resp = task.stop_task('task_id')
        """
        resp = self.__do_task('PUT', id, operation='tasks')
        return StopTaskResult(resp)

    def restart_task(self, id):
        """
        usage
             >>> resp = task.restart_task('task_id')
        """
        target = id + '/restart'
        resp = self.__do_task('PUT', target, operation='tasks')
        return RestartTaskResult(resp)

    def get_jobs(self, id):
        """
        usage:
            >>> resp = task.get_jobs('task_id')
        """
        target = id + '/jobs'
        resp = self.__do_task('GET', target, operation='tasks')
        return self._parse_result(resp, yml_utils.parse_get_jobs, GetJobResult)

    def get_job_cmd(self, id):
        """
        usage:
            >>> resp = task.get_job_cmd('job_id')
        """
        task_id = id.split('_')[0]
        target = task_id + '/cmd/' + id
        resp = self.__do_task('GET', target, operation='tasks')
        return GetJobCmdResult(resp)

    def get_job_info(self, id):
        """
        usage:
            >>> resp = task.get_job_info('job_id')
        """
        task_id = id.split('_')[0]
        target = task_id + '/jobs/' + id
        resp = self.__do_task('GET', target, operation='tasks')
        return GetJobInfoResult(resp)


class Workflows(_Base):
    """ 用于Workflows操作的类
    :param auth: 包含了用户认证信息的Auth对象
    :type auth: gdpy.GeneDockAuth

    :param str endpoint: 访问域名，如北京区域的域名为cn-beijing-api.genedock.com
    :param str res_account_name: 指定从该账号下获取资源(如需获取公共资源，则为public)
    :param str res_project_name: 指定从该项目下获取资源(默认为default)
    :raises: 如果获取或上传失败，则抛出来自服务端的异常; 还可能抛出其他异常
    workflows related operations
    usage::
        >>> import gdpy
        >>> auth = gdpy.GeneDockAuth('access_key_id', 'access_key_secret')
        >>> workflow = gdpy.Workflows(auth, 'https://cn-beijing-api.genedock.com', 'res_account_name', 'project_name')
    """
    def __init__(self, auth, endpoint, res_account_name, project_name='default', connect_timeout=None):
        super(Workflows, self).__init__(auth, endpoint, connect_timeout)
        self.res_account_name = res_account_name
        self.res_project_name = project_name

    def __do_workflow(self, method, name=None, version=None, **kwargs):
        if name is not None and not is_object_name_valid(name):
            raise ValueError("Invalid workflow name! Expect a string started with alphabet and under 128 characters, but got {}!".format(str(name)))
        if version is not None and not is_object_version_valid(version):
            raise ValueError("Invalid workflow version! Expect interger greater than 0, but got {}".format(str(version)))
        return self._do(method, self.res_account_name, self.res_project_name, name, workflow_version=version, **kwargs)

    def list_workflows(self):
        """
        usage:
            >>> resp = workflow.list_workflows()
        """
        resp = self.__do_workflow('GET', operation='workflows')
        return self._parse_result(resp, yml_utils.parse_list_workflows, ListWorkflowsResult)

    def list_exc_workflows(self):
        """
        usage:
            >>> resp = workflow.list_exc_workflows()
        """
        resp = self.__do_workflow('GET', operation='executable-workflows')
        return self._parse_result(resp, yml_utils.parse_list_workflows, ListWorkflowsResult)

    def get_workflow(self, name, version=None):
        """
        usage:
            >>> resp = workflow.get_workflow('workflow_name', 'workflow_version')
            */Or lack version/*
            >>> resp = workflow.get_workflow('workflow_name')
        """
        if name is None:
            raise ValueError("Expect a name(str) started with alphabet and under 128 characters")
        resp = self.__do_workflow('GET', name, version, operation='workflows')
        return GetWorkflowResult(resp)

    def get_exc_workflow(self, name, version):
        """
        usage:
            >>> resp = workflow.get_exc_workflow('workflow_name', 'workflow_version')
        """
        if name is None:
            raise ValueError("Expect a name(str) started with alphabet and under 128 characters")
        if version is None:
            raise ValueError("Expect interger greater than 0 as version")
        resp = self.__do_workflow('GET', name, version, operation='executable-workflows')
        return GetExcWorkflowResult(resp)

        """
        get a yaml tempalte:
            >>> from gdpy.yml_utils import yaml_dumper
            >>> yml_template = yaml_dumper(resp.parameter)
        """

    def delete_workflow(self, name, version):
        """
        usage:
            >>> resp = workflow.delete_workflow('workflow_name', 'workflow_version')
        """
        if name is None:
            raise ValueError("Expect a name(str) started with alphabet and under 128 characters")
        if version is None:
            raise ValueError("Expect interger greater than 0 as version")
        resp = self.__do_workflow('DELETE', name, version, operation='workflows')
        return DeleteWorkflowResult(resp)

    def create_workflow(self, name, version, description=''):
        """
        usage:
            >>> resp = workflow.create_workflow('workflow_name', 'workflow_version', 'description')
        """
        if not is_object_name_valid(name):
            raise ValueError("Invalid workflow name! Expect a string started with alphabet and under 128 characters, but got {}!".format(str(name)))
        if not is_object_version_valid(version):
            raise ValueError("Invalid workflow version! Expect interger greater than 0, but got {}".format(str(version)))
        data = {"workflow_name": name, "workflow_version": version, "description": description}
        resp = self.__do_workflow('POST', data=data, operation='workflows')
        return CreateWorkflowResult(resp)

    def put_workflow(self, param_file):
        """
        usage:
            >>> resp = workflow.put_workflow('parameter_file_path')
        """
        workflow_temp = yml_utils.yaml_loader(param_file)
        workflow_description = workflow_temp.get('workflow').get('description', '')
        if not is_object_name_valid(workflow_temp.get('workflow').get('name')):
            raise ValueError("Invalid workflow name! Expect a string started with alphabet and under 128 characters, but got {}!".format(str(workflow_temp.get('workflow').get('name'))))
        else:
            workflow_name = str(workflow_temp.get('workflow').get('name'))
        if not is_object_version_valid(workflow_temp.get('workflow').get('version')):
            raise ValueError("Invalid tool version! Expect interger greater than 0, but got {}".format(str(workflow_temp.get('workflow').get('version'))))
        else:
            workflow_version = int(workflow_temp.get('workflow').get('version'))
        workflow_configs = {'nodelist': workflow_temp.get('workflow').get('nodelist')}
        try:
            data = dict()
            data["workflow_version"] = workflow_version
            data["configs"] = workflow_configs
            data["description"] = workflow_description
            resp = self.__do_workflow('PUT', workflow_name, data=data, operation='workflows')
        except ValueError as e:
            raise e
        return PutWorkflowResult(resp)

    def set_workflow_param(self, param_file, name, version):
        """
        usage:
            >>> resp = workflow.set_workflow_param('exec_workflow_param_file', 'workflow_name', 'workflow_version')
        """
        if not is_object_name_valid(name):
            raise ValueError("Invalid workflow name! Expect a string started with alphabet and under 128 characters, but got {}!".format(str(name)))
        if not is_object_version_valid(version):
            raise ValueError("Invalid workflow version! Expect interger greater than 0, but got {}".format(str(version)))
        workflow_temp = yml_utils.yaml_loader(param_file)
        data = {'workflow_version': version, 'parameters': workflow_temp}
        resp = self.__do_workflow('PUT', name, data=data, operation='executable-workflows')
        return SetWorkflowParamResult(resp)


class Tools(_Base):
    """ 用于Tools操作的类
    :param auth: 包含了用户认证信息的Auth对象
    :type auth: gdpy.GeneDockAuth

    :param str endpoint: 访问域名，如北京区域的域名为cn-beijing-api.genedock.com
    :param str res_account_name: 指定从该账号下获取资源(如需获取公共资源，则为public)
    :param str res_project_name: 指定从该项目下获取资源(默认为default)
    :raises: 如果获取或上传失败，则抛出来自服务端的异常; 还可能抛出其他异常
    tools related operations
    usage::
        >>> import gdpy
        >>> auth = gdpy.GeneDockAuth('access_key_id', 'access_key_secret')
        >>> tool = gdpy.Tools(auth, 'https://cn-beijing-api.genedock.com', 'res_account_name', 'project_name')
    """
    def __init__(self, auth, endpoint, res_account_name, project_name='default', connect_timeout=None):
        super(Tools, self).__init__(auth, endpoint, connect_timeout)
        self.res_account_name = res_account_name
        self.res_project_name = project_name

    def __do_tool(self, method, name=None, version=None, **kwargs):
        if name is not None and not is_object_name_valid(name):
            raise ValueError("Invalid tool name! Expect a string started with alphabet and under 128 characters, but got {}!".format(str(name)))
        if version is not None and not is_object_version_valid(version):
            raise ValueError("Invalid tool version! Expect interger greater than 0, but got {}".format(str(version)))
        return self._do(method, self.res_account_name, self.res_project_name, name, tool_version=version, **kwargs)

    def get_tool(self, name, version=None):
        """
        usage:
            >>> resp = tool.get_tool('tool_name', 'tool_version')
            */Or lack version/*
            >>> resp = tool.get_tool('tool_name')
        """
        if name is None:
            raise ValueError("Expect a name(str) started with alphabet and under 128 characters")
        resp = self.__do_tool('GET', name, version, operation='tools')
        return GetToolResult(resp)

    def list_tools(self):
        """
        usage:
            >>> resp = tool.list_tools()
        """
        resp = self.__do_tool('GET', operation='tools')
        return self._parse_result(resp, yml_utils.parse_list_tools, ListToolResult)

    def get_tool_param(self, name, version=None):
        """
        usage:
            >>> resp = tool.get_tool_param('tool_name', 'tool_version')
            */Or lack version/*
            >>> resp = tool.get_tool_param('tool_name')
        """
        if name is None:
            raise ValueError("Expect a name(str) started with alphabet and under 128 characters")
        resp = self.__do_tool('GET', name, version, operation='toolparameters')
        return self._parse_result(resp, yml_utils.parse_get_tool_parameters, GetToolParamResult)

    def delete_tool(self, name, version):
        """
        usage:
            >>> resp = tool.delete_tool('tool_name', 'tool_version')
        """
        if name is None:
            raise ValueError("Expect a name(str) started with alphabet and under 128 characters")
        if version is None:
            raise ValueError("Expect interger greater than 0 as version")
        resp = self.__do_tool('DELETE', name, version, operation='tools')
        return DeleteToolResult(resp)

    def create_tool(self, name, version, description=''):
        """
        usage:
            >>> resp = tool.create_tool('tool_name', 'tool_version', 'description')
        """
        if not is_object_name_valid(name):
            raise ValueError("Invalid tool name! Expect a string started with alphabet and under 128 characters, but got {}!".format(str(name)))
        if not is_object_version_valid(version):
            raise ValueError("Invalid tool version! Expect interger greater than 0, but got {}".format(str(version)))
        data = {"tool_name": name, "tool_version": version, "description": description}
        resp = self.__do_tool('POST', data=data, operation='tools')
        return CreateToolResult(resp)

    def put_tool(self, param_file):
        """
        usage:
            >>> resp = tool.put_tool('parameter_file_path')
        """
        tool_temp = yml_utils.yaml_loader(param_file)
        tool_description = tool_temp.get('app').get('description', '')
        if not is_object_name_valid(tool_temp.get('app').get('name')):
            raise ValueError("Invalid tool name! Expect a string started with alphabet and under 128 characters, but got {}!".format(str(name)))
        else:
            tool_name = str(tool_temp.get('app').get('name'))
        if not is_object_version_valid(tool_temp.get('app').get('version')):
            raise ValueError("Invalid tool version! Expect interger greater than 0, but got {}".format(str(version)))
        else:
            tool_version = int(tool_temp.get('app').get('version'))
        tool_configs = tool_temp.get('app')
        try:
            data = dict()
            data["tool_version"] = tool_version
            data["configs"] = tool_configs
            data["description"] = tool_description
            resp = self.__do_tool('PUT', tool_name, data=data, operation='tools')
        except ValueError as e:
            raise e
        return PutToolResult(resp)


class Data(_Base):
    """ 用于Data操作的类
    :param auth: 包含了用户认证信息的Auth对象
    :type auth: gdpy.GeneDockAuth

    :param str endpoint: 访问域名，如北京区域的域名为cn-beijing-api.genedock.com
    :param str res_account_name: 指定从该账号下获取资源(如需获取公共资源，则为public)
    :param str res_project_name: 指定从该项目下获取资源(默认为default)
    :raises: 抛出异常
    data related operations
    usage::
        >>> import gdpy
        >>> auth = gdpy.GeneDockAuth('access_key_id', 'access_key_secret')
        >>> data = gdpy.Data(auth, 'https://cn-beijing-api.genedock.com', 'res_account_name', 'project_name')
    """
    def __init__(self, auth, endpoint, res_account_name, project_name='default', connect_timeout=None):
        super(Data, self).__init__(auth, endpoint, connect_timeout)
        self.res_account_name = res_account_name
        self.res_project_name = project_name

    def __do_data(self, method, data_path=None, **kwargs):
        return self._do(method, self.res_account_name, self.res_project_name, data_path,  **kwargs)

    def archive_data(self, data_path=None):
        """
        usage:
            >>> resp = data.archive_data('data_path')
        """
        if data_path is None:
            raise ValueError("Expect a date path")
        resp = self.__do_data('POST', data_path, operation='archive', end_slash=0)
        return ArchiveDataResult(resp)

    def restore_data(self, data_path=None):
        """
        usage:
            >>> resp = data.restore_data('data_path')
        """
        if data_path is None:
            raise ValueError("Expect a date path")
        resp = self.__do_data('POST', data_path, operation='restore', end_slash=0)
        return RestoreDataResult(resp)