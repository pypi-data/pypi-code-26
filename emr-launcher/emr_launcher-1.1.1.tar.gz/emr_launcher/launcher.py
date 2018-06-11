import boto3
import json
from jinja2 import Template
import emr_launcher
import logging
from datetime import datetime, timedelta
import pkgutil
from importlib import import_module
import re

logger = logging.getLogger("emr_launcher")


class EmrLauncher(object):

    def run(
        self,
        config,
        job_id=None,
        name=None,
        dry_run=False,
        distinct=False,
        replace_existing_cluster=False
    ):
        """
        Args:
            config                   - dict config matching parameters here:
                                       http://boto3.readthedocs.io/en/latest/reference/services/emr.html#EMR.Client.run_job_flow
            job_id                   - optional EMR job_id. When set, adds steps in config['Steps']
                                       to an existing cluster. If None, starts a new cluster
            name                     - overrides the name of the cluster
            distinct                 - Will only launch the job if another cluster of the
                                      same name is *not* running. Otherwise, will throw an error
            replace_existing_cluster - Will shut down a single existing cluster
        """

        client = boto3.client('emr', region_name='us-east-1')
        config['Name'] = name if name else config['Name']

        if dry_run:
            print json.dumps(config, indent=4)

        if replace_existing_cluster:
            clusters = [cluster for cluster in find_clusters_with(client, name=config['Name'], created_after=datetime.utcnow() - timedelta(days=365), cluster_states=['STARTING', 'BOOTSTRAPPING', 'RUNNING'])]
            if replace_existing_cluster:
                if len(clusters) > 1:
                    raise Exception('Cannot replace cluster because more than 1 cluster with the same name exists. Cluster IDs are the following: ' + ','.join([cluster.get('Id', '<id-not-found>') for cluster in clusters]))

                elif len(clusters) == 1:
                    logger.info("Killing cluster with ID: %s..." % clusters[0].get('Id'))
                    if not dry_run:
                        client.terminate_job_flows(JobFlowIds=[clusters[0].get('Id')])
                    logger.info("Killed.")
                elif len(clusters) == 0:
                    logger.info("No existing cluster to replace.")

        if distinct:
            clusters = [cluster for cluster in find_clusters_with(client, name=config['Name'], created_after=datetime.utcnow() - timedelta(days=365), cluster_states=['STARTING', 'BOOTSTRAPPING', 'RUNNING'])]
            if len(clusters) > 0:
                for cluster in clusters:
                    logger.error('Cluster already running with name: \'%s\' and Id: \'%s\'', cluster.get('Name', 'Not Found'), cluster.get('Id', '<id-not-found>'))
                raise Exception('Cannot launch cluster with the name %s, because another cluster of the same name is already running. If this is not your intention, remove the --distinct flag when using emr_launcher' % config.get('Name', '<NAME_NOT_FOUND>'))

        if not job_id:
            job_flow_id = 'N/A (due to dry-run)'
            if not dry_run:
                job_flow_id = client.run_job_flow(**config).get('JobFlowId')
            logger.info('Job started with job-id: %s', job_flow_id)
        else:
            if not dry_run:
                client.add_job_flow_steps(JobFlowId=job_id, Steps=config['Steps'])
            logger.info('Steps added to job-id: %s', job_id)


def get_modules():
    modules = [('emr_launcher', emr_launcher)]
    # import plugin modules, any module in the current namespace which begins with
    # 'emr_launcher_' will be included in the function set
    modules.extend([
        (re.sub('^emr_launcher_', '', name), import_module(name))
        for (module, name, ispkg)
        in pkgutil.iter_modules()
        if name.startswith("emr_launcher_")
    ])
    return modules


def render_template(config):
    """
        Args:
            config - string config with jinja2 template substitution clauses.
        Return:
            string - configuration with template values rendered
    """
    template = Template(config)

    for (name, module) in get_modules():
        template.globals[name] = module

    # render the template
    return template.render()


def find_clusters_with(client, name, created_after, cluster_states):
    """
        finds emr clusters with exact match of <name>
        and created after <created_after>
        Args:
            client - EMR.Client
            name - name of the clusters to be found
            created_after - datetime.datetime how far to search back
        Return:
            a list of cluster information matching the name and time parameters
    """
    clusters = []
    marker = None
    params = dict(CreatedAfter=created_after, ClusterStates=cluster_states)
    while True:
        res = client.list_clusters(**params)
        clusters += res.get('Clusters', [])
        if not res.get('Marker', None):
            break

        params['Marker'] = res.get('Marker', None)

    return [cluster for cluster in clusters if cluster['Name'] == name]
