# Copyright 2018 Globo.com
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import click
import prettytable
import json

from faasclient import client
from requests.packages import urllib3


# Disable HTTPS verification warnings.
urllib3.disable_warnings()


OS_USERNAME_HELP = ('Name used for authentication with the OpenStack Identity '
                    'service. Defaults to env[OS_USERNAME].')

OS_PASSWORD_HELP = ('Password used for authentication with the OpenStack '
                    'Identity service. Defaults to env[OS_PASSWORD].')

OS_TENANT_NAME_HELP = ('Tenant to request authorization on. Defaults to '
                       'env[OS_TENANT_NAME].')

OS_AUTH_URL_HELP = ('Specify the Identity endpoint to use for authentication. '
                    'Defaults to env[OS_AUTH_URL].')


@click.group(context_settings={'help_option_names': ['-h', '--help']})
@click.option('--os-username', envvar='OS_USERNAME', help=OS_USERNAME_HELP,
              metavar='<auth-user-name>')
@click.option('--os-password', envvar='OS_PASSWORD', help=OS_PASSWORD_HELP,
              metavar='<auth-password>')
@click.option('--os-tenant-name', envvar='OS_TENANT_NAME',
              help=OS_TENANT_NAME_HELP, metavar='<auth-tenant-name>')
@click.option('--os-auth-url', envvar='OS_AUTH_URL', help=OS_AUTH_URL_HELP,
              metavar='<auth-url>')
@click.pass_context
def cli(ctx, os_username, os_password, os_tenant_name, os_auth_url):

    conn = client.Client(authurl=os_auth_url,
                         user=os_username,
                         key=os_password,
                         tenant_name=os_tenant_name,
                         insecure=True)

    ctx.obj = {'CONN': conn}


# ACCESS ----------------------------------------------------------------------
@cli.command(name='access-list')
@click.option('export_id', '--export-id', metavar='<export_id or export_path>',
              type=click.INT, required=True)
@click.pass_context
def access_list(ctx, export_id):
    conn = ctx.obj['CONN']
    print_response(conn.access_list(export_id))


@cli.command(name='access-get')
@click.option('--export-id', metavar='<export_id or export_path>',
              type=click.INT, required=True)
@click.option('--access-id', metavar='<access_id>',
              type=click.INT, required=True)
@click.pass_context
def access_get(ctx, export_id, access_id):
    conn = ctx.obj['CONN']
    print_response(conn.access_get(export_id, access_id))


@cli.command(name='access-create')
@click.option('--export-id', metavar='<export_id or export_path>',
              type=click.INT, required=True)
@click.option('--permission', metavar='<permission>', type=click.STRING,
              required=True)
@click.option('--host', metavar='<host>', type=click.STRING, required=True)
@click.pass_context
def access_create(ctx, export_id, permission, host):
    conn = ctx.obj['CONN']
    print_response(conn.access_create(export_id, permission, host))


@cli.command(name='access-delete')
@click.option('--export-id', metavar='<export_id or export_path>',
              type=click.INT, required=True)
@click.option('--access-id', metavar='<access_id>',
              type=click.INT, required=True)
@click.pass_context
def access_delete(ctx, export_id, access_id):
    conn = ctx.obj['CONN']
    print_response(conn.access_delete(export_id, access_id))


# CATEGORIA -------------------------------------------------------------------
@cli.command(name='categoria-list')
@click.pass_context
def categoria_list(ctx):
    conn = ctx.obj['CONN']
    print_response(conn.categoria_list())


@cli.command(name='categoria-create')
@click.option('--name', metavar='<categoria-name>', type=click.STRING,
              required=True)
@click.pass_context
def categoria_create(ctx, name):
    conn = ctx.obj['CONN']
    print_response(conn.categoria_create(name))


@cli.command(name='categoria-get')
@click.option('categoria_id', '--id', metavar='<categoria_id>', type=click.INT,
              required=True)
@click.pass_context
def categoria_get(ctx, categoria_id):
    conn = ctx.obj['CONN']
    print_response(conn.categoria_get(categoria_id))


@cli.command(name='categoria-update')
@click.option('categoria_id', '--id', metavar='<categoria_id>', type=click.INT,
              required=True)
@click.option('--name', metavar='<categoria_name>', type=click.STRING,
              required=True)
@click.pass_context
def categoria_update(ctx, categoria_id, name):
    conn = ctx.obj['CONN']
    print_response(conn.categoria_update(categoria_id, name))


@cli.command(name='categoria-delete')
@click.option('categoria_id', '--id', metavar='<categoria_id>', type=click.INT,
              required=True)
@click.pass_context
def categoria_delete(ctx, categoria_id):
    conn = ctx.obj['CONN']
    print_response(conn.categoria_delete(categoria_id))


# AUDIT ------------------------------------------------------------------------
@cli.command(name='audit-list')
@click.pass_context
def audit_list(ctx):
    conn = ctx.obj['CONN']
    print_response(conn.audit_list())


@cli.command(name='audit-get')
@click.option('audit_id', '--id', metavar='<audit_id>', type=click.INT,
              required=True)
@click.pass_context
def audit_get(ctx, audit_id):
    conn = ctx.obj['CONN']
    print_response(conn.audit_get(audit_id))


@cli.command(name='audit-export-get')
@click.option('export_id', '--export-id', metavar='<export_id>', type=click.INT,
              required=True)
@click.pass_context
def audit_export_get(ctx, export_id):
    conn = ctx.obj['CONN']
    print_response(conn.audit_export_get(export_id))


# apphost ----------------------------------------------------------------
@cli.command(name='apphost-list')
@click.pass_context
def apphost_list(ctx):
    conn = ctx.obj['CONN']
    print_response(conn.apphost_list())


@cli.command(name='apphost-create')
@click.option('--ip', metavar='<apphost_ip>', type=click.STRING,
              required=True)
@click.option('--hostname', metavar='<apphost_hostname>',
              type=click.INT, required=True)
@click.pass_context
def apphost_create(ctx, ip, hostname):
    conn = ctx.obj['CONN']
    print_response(conn.apphost_create(ip, hostname))


@cli.command(name='apphost-update')
@click.option('apphost_id', '--id', metavar='<apphost_id>',
              type=click.INT, required=True)
@click.option('--ip', metavar='<apphost_ip>', type=click.STRING,
              required=True)
@click.option('--hostname', metavar='<apphost_hostname>',
              type=click.STRING, required=True)
@click.pass_context
def apphost_update(ctx, apphost_id, ip, hostname):
    conn = ctx.obj['CONN']
    print_response(conn.apphost_update(apphost_id, ip, hostname))


@cli.command(name='apphost-get')
@click.option('apphost_id', '--id', metavar='<apphost_id>',
              type=click.INT, required=True)
@click.pass_context
def apphost_get(ctx, apphost_id):
    conn = ctx.obj['CONN']
    print_response(conn.apphost_get(apphost_id))


@cli.command(name='apphost-delete')
@click.option('apphost_id', '--id', metavar='<apphost_id>',
              type=click.INT, required=True)
@click.pass_context
def apphost_delete(ctx, apphost_id):
    conn = ctx.obj['CONN']
    print_response(conn.apphost_delete(apphost_id))


# EXPORT ----------------------------------------------------------------------
@cli.command(name='export-list')
@click.option('host', '--host', metavar='<host>', type=click.STRING,
              required=False)
@click.pass_context
def export_list(ctx, host):
    conn = ctx.obj['CONN']
    print_response(conn.export_list(host))


@cli.command(name='project-quota-get')
@click.pass_context
def export_get(ctx):
    conn = ctx.obj['CONN']
    print_response(conn.project_quota_get())


@cli.command(name='export-get')
@click.option('export_id', '--id', metavar='<export_id or export_path>',
              type=click.STRING, required=True)
@click.pass_context
def export_get(ctx, export_id):
    conn = ctx.obj['CONN']
    print_response(conn.export_get(export_id))


@cli.command(name='export-create')
@click.option('--quota', metavar='<size in KB>', type=click.INT, required=True)
@click.option('--categoria', metavar='<categoria>', type=click.INT,
              required=True)
@click.option('--resource_id', metavar='<resource_id>', type=click.STRING,
              required=False)
@click.option('--time-id', metavar='<time_id>', type=click.STRING,
              required=False)
@click.pass_context
def export_create(ctx, quota, categoria, resource_id, time_id):
    conn = ctx.obj['CONN']
    print_response(conn.export_create(quota, categoria, resource_id, time_id))


@cli.command(name='export-delete')
@click.option('export_id', '--id', metavar='<export_id or export_path>',
              type=click.INT, required=True)
@click.option('--force', is_flag=True)
@click.pass_context
def export_delete(ctx, export_id, force):
    conn = ctx.obj['CONN']
    if force:
        print_response(conn.export_force_delete(export_id))
    else:
        print_response(conn.export_delete(export_id))


@cli.command(name='export-delete')
@click.option('export_id', '--id', metavar='<export_id or export_path>',
              type=click.INT, required=True)
@click.option('--force', is_flag=True)
@click.pass_context
def export_delete(ctx, export_id, force):
    conn = ctx.obj['CONN']
    if force:
        print_response(conn.export_force_delete(export_id))
    else:
        print_response(conn.export_delete(export_id))


@cli.command(name='group-exports')
@click.option('exports_id', '--id', multiple=True, metavar='<export_id or export_path>',
              type=click.INT, required=True)
@click.option('resource_id', '--resource-id', metavar='<resource_id>',
              type=click.STRING, required=True)
@click.pass_context
def export_group(ctx, exports_id, resource_id):
    conn = ctx.obj['CONN']
    print_response(conn.export_group(exports_id, resource_id))


@cli.command(name='time-exports')
@click.option('exports_id', '--id', multiple=True, metavar='<export_id or export_path>',
              type=click.INT, required=True)
@click.option('time_id', '--time-id', metavar='<time_id>',
              type=click.STRING, required=True)
@click.pass_context
def exports_time(ctx, exports_id, time_id):
    conn = ctx.obj['CONN']
    print_response(conn.exports_time(exports_id, time_id))


# FILER -----------------------------------------------------------------------
@cli.command(name='filer-list')
@click.pass_context
def filer_list(ctx):
    conn = ctx.obj['CONN']
    print_response(conn.filer_list())


@cli.command(name='filer-create')
@click.option('--vfiler', metavar='<vfiler>', type=click.STRING, required=True)
@click.option('--export-filer', metavar='<export_filer>', type=click.STRING,
              required=True)
@click.option('connection_filer', '--conn', metavar='<connection_filer>',
              type=click.STRING, required=True)
@click.option('--username', metavar='<username>', type=click.STRING,
              required=True)
@click.option('--password', metavar='<password>', type=click.STRING,
              required=True)
@click.pass_context
def filer_create(ctx, vfiler, export_filer, connection_filer, username,
                 password):
    conn = ctx.obj['CONN']
    response = conn.filer_create(vfiler, export_filer, connection_filer,
                                 username, password)
    print_response(response)


@cli.command(name='filer-get')
@click.option('filer_id', '--id', metavar='<filer_id>', required=True)
@click.pass_context
def filer_get(ctx, filer_id):
    conn = ctx.obj['CONN']
    print_response(conn.filer_get(filer_id))


@cli.command(name='filer-delete')
@click.option('filer_id', '--id', metavar='<filer_id>', required=True)
@click.pass_context
def filer_delete(ctx, filer_id):
    conn = ctx.obj['CONN']
    print_response(conn.filer_delete(filer_id))


@cli.command(name='filer-update')
@click.option('filer_id', '--id', metavar='<filer_id>', type=click.INT,
              required=True)
@click.option('--vfiler', metavar='<vfiler>', type=click.STRING, required=True)
@click.option('--export-filer', metavar='<export_filer>', type=click.STRING,
              required=True)
@click.option('connection_filer', '--conn', metavar='<connection_filer>',
              type=click.STRING, required=True)
@click.option('--username', metavar='<username>', type=click.STRING,
              required=True)
@click.option('--password', metavar='<password>', type=click.STRING,
              required=True)
@click.pass_context
def filer_update(ctx, filer_id, vfiler, export_filer, connection_filer,
                 username, password):
    conn = ctx.obj['CONN']
    response = conn.filer_update(filer_id, vfiler, export_filer, conn,
                                 username,
                                 password)
    print_response(response)


# VOLUME ----------------------------------------------------------------------
@cli.command(name='volume-list')
@click.pass_context
def volume_list(ctx):
    conn = ctx.obj['CONN']
    print_response(conn.volume_list())


@cli.command(name='volume-create')
@click.option('--path', metavar='<path>', type=click.STRING, required=True)
@click.option('filer_id', '--filer-id', metavar='<filer_id>', type=click.INT,
              required=True)
@click.option('categoria_id', '--categoria-id', metavar='<categoria_id>',
              type=click.INT, required=True)
@click.option('--max', metavar='<maxsnapshots>', type=click.INT, required=True)
@click.pass_context
def volume_create(ctx, path, filer_id, categoria_id, max):
    conn = ctx.obj['CONN']
    print_response(conn.volume_create(path, filer_id, categoria_id, max))


@cli.command(name='volume-get')
@click.option('volume_id', '--id', metavar='<volume_id>', type=click.INT,
              required=True)
@click.pass_context
def volume_get(ctx, volume_id):
    conn = ctx.obj['CONN']
    print_response(conn.volume_get(volume_id))


@cli.command(name='volume-delete')
@click.option('volume_id', '--id', metavar='<volume_id>', type=click.INT,
              required=True)
@click.pass_context
def volume_delete(ctx, volume_id):
    conn = ctx.obj['CONN']
    print_response(conn.volume_delete(volume_id))


@cli.command(name='volume-update')
@click.option('volume_id', '--id', metavar='<volume_id>', type=click.INT,
              required=True)
@click.option('--path', metavar='<path>', type=click.STRING, required=True)
@click.option('filer_id', '--filer-id', metavar='<filer_id>', type=click.INT,
              required=True)
@click.option('categoria_id', '--categoria-id', metavar='<categoria_id>',
              type=click.INT, required=True)
@click.option('--max', metavar='<maxsnapshots>', type=click.INT, required=True)
@click.pass_context
def volume_update(ctx, volume_id, path, filer_id, categoria_id, maxsnapshots):
    conn = ctx.obj['CONN']
    print_response(conn.volume_update(volume_id, path, filer_id, categoria_id,
                                      maxsnapshots))


@cli.command(name='volumes-info')
@click.pass_context
def volumes_info(ctx):
    conn = ctx.obj['CONN']
    print_response(conn.volumes_info())


@cli.command(name='volumes-info-update')
@click.pass_context
def volumes_update_info(ctx):
    conn = ctx.obj['CONN']
    print_response(conn.volumes_update_info())


# PERMISSION ------------------------------------------------------------------
@cli.command(name='permission-list')
@click.pass_context
def permission_list(ctx):
    conn = ctx.obj['CONN']
    print_response(conn.permission_list())


@cli.command(name='permission-create')
@click.option('--name', metavar='<permission_name>', type=click.STRING,
              required=True)
@click.pass_context
def permission_create(ctx, name):
    conn = ctx.obj['CONN']
    print_response(conn.permission_create(name))


@cli.command(name='permission-update')
@click.option('permission_id', '--id', metavar='<permission_id>',
              type=click.INT, required=True)
@click.option('--name', metavar='<permission_name>', type=click.STRING,
              required=True)
@click.pass_context
def permission_update(ctx, permission_id, name):
    conn = ctx.obj['CONN']
    print_response(conn.permission_update(permission_id, name))


@cli.command(name='permission-get')
@click.option('permission_id', '--id', metavar='<permission_id>',
              type=click.INT, required=True)
@click.pass_context
def permission_get(ctx, permission_id):
    conn = ctx.obj['CONN']
    print_response(conn.permission_get(permission_id))


@cli.command(name='permission-delete')
@click.option('permission_id', '--id', metavar='<permission_id>',
              type=click.INT, required=True)
@click.pass_context
def permission_delete(ctx, permission_id):
    conn = ctx.obj['CONN']
    print_response(conn.permission_delete(permission_id))


# QUOTA -----------------------------------------------------------------------
@cli.command(name='quota-get')
@click.option('export_id', '--export-id', metavar='<export_id>',
              type=click.INT, required=False)
@click.pass_context
def quota_get(ctx, export_id):
    conn = ctx.obj['CONN']
    print_response(conn.quota_get(export_id))


@cli.command(name='quota-set')
@click.option('export_id', '--export-id', metavar='<export_id>',
              type=click.INT, required=True)
@click.option('--size', metavar='<size in KB>', type=click.INT, required=True)
@click.pass_context
def quota_set(ctx, export_id, size):
    conn = ctx.obj['CONN']
    print_response(conn.export_update(export_id, size))


@cli.command(name='quota-delete')
@click.option('export_id', '--export-id', metavar='<export_id>',
              type=click.INT, required=True)
@click.pass_context
def quota_delete(ctx, export_id):
    conn = ctx.obj['CONN']
    print_response(conn.quota_delete(export_id))


# JOBS / RESTORE --------------------------------------------------------------
@cli.command(name='job-list')
@click.pass_context
def job_list(ctx):
    conn = ctx.obj['CONN']
    print_response(conn.jobs_list())


@cli.command(name='job-get')
@click.option('job_id', '--id', metavar='<job_id>', type=click.STRING,
              required=True)
@click.pass_context
def job_get(ctx, job_id):
    conn = ctx.obj['CONN']
    print_response(conn.jobs_get(job_id))


# SNAPSHOTS -----------------------------------------------------------------
@cli.command(name='snapshot-list')
@click.option('export_id', '--export-id', metavar='<export_id or export_path>',
              type=click.INT, required=True)
@click.pass_context
def snapshot_list(ctx, export_id):
    conn = ctx.obj['CONN']
    print_snapshot_list(conn.snapshot_list(export_id))


@cli.command(name='snapshot-create')
@click.option('--export-id', metavar='<export_id or export_path>',
              type=click.INT, required=True)
@click.pass_context
def snapshot_create(ctx, export_id):
    conn = ctx.obj['CONN']
    print_response(conn.snapshot_create(export_id))


@cli.command(name='snapshot-get')
@click.option('--export-id', metavar='<export_id or export_path>',
              type=click.INT, required=True)
@click.option('--snapshot-id', metavar='<snapshot_id>', type=click.INT,
              required=True)
@click.pass_context
def snapshot_get(ctx, export_id, snapshot_id):
    conn = ctx.obj['CONN']
    print_response(conn.snapshot_get(export_id, snapshot_id))


@cli.command(name='snapshot-delete')
@click.option('export_id', '--export-id', metavar='<export_id or export_path>',
              type=click.INT, required=True)
@click.option('snapshot_id', '--snapshot-id', metavar='<snapshot_id>',
              type=click.INT, required=True)
@click.pass_context
def snapshot_delete(ctx, export_id, snapshot_id):
    conn = ctx.obj['CONN']
    print_response(conn.snapshot_delete(export_id, snapshot_id))


@cli.command(name='snapshot-restore')
@click.option('export_id', '--export-id', metavar='<export_id or export_path>',
              type=click.INT, required=True)
@click.option('snapshot_id', '--snapshot-id', metavar='<snapshot_id>',
              type=click.INT, required=True)
@click.pass_context
def snapshot_restore(ctx, export_id, snapshot_id):
    conn = ctx.obj['CONN']
    print_response(conn.snapshot_restore(export_id, snapshot_id))

# REPORT TO GLOBOMAP --------------------------------------------------------------
@cli.command(name='report-get')
@click.pass_context
def report_get(ctx):
    conn = ctx.obj['CONN']
    print json.dumps(conn.report_get())


# PRINTS -----------------------------------------------------------------
def print_response(response):

    _, content = response

    if type(content) is list or type(content) is dict:
        print_list(content)
    else:
        print_message(response)


def print_list(content):

    if len(content) == 0:
        click.echo('No results found!')
        return

    if type(content) is dict:
        content = [content]

    fields = sorted(content[0].keys())

    pt = prettytable.PrettyTable([f for f in fields], caching=False)

    for o in content:
        row = []
        for field in fields:
            row.append(o[field])
        pt.add_row(row)

    click.echo(pt.get_string(sortby=fields[0]))


# The dictionary does not have a standard keys! Because it was implemented a
# specific printing method for this case. [There are system snapshots and User
# and only users have id key]
def print_snapshot_list(response):

    _, content = response

    if len(content) == 0:
        click.echo('No results found!')
        return

    if type(content) is dict:
        content = [content]

    keys = sorted(content[0].keys())

    pt = prettytable.PrettyTable([f for f in keys], caching=False)

    for o in content:
        row = []
        for key in keys:
            if 'id' in o:
                row.append(o[key])
            else:
                if key == 'id':
                    row.append('')
                else:
                    row.append(o[key])
        pt.add_row(row)

    click.echo(pt.get_string(sortby=keys[0]))


def print_message(response):
    status_code, content = response

    if status_code in (200, 201):
        content = content or 'Success!'  # For operations return empty response
        click.echo(content)
    else:
        content = content or 'Error!'  # Some operations return empty response
        click.echo('%s (HTTP %d)' % (content, status_code))


if __name__ == '__main__':
    cli(obj={})
