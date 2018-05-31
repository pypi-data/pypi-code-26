from urlobject import URLObject
from st_library.utils.helpers.store import Store


ROOT = URLObject(Store.host)

METADATA_ENDPOINT = ROOT.add_path('api/metadata/')
EXECUTION_METADATA_ENDPOINT = ROOT.add_path('api/execution-metadata/')
LOGGING_ENDPOINT = ROOT.add_path('api/logging/')
DATA_ENDPOINT = ROOT.add_path('api/data')

GETTOKEN_ENDPOINT = ROOT.add_path('api/uaa/api-keys/')


PERFORMANCES_LIST_GET_PATH = EXECUTION_METADATA_ENDPOINT.add_path('v2/performances/')

def sec_get_token(uuid):
    return GETTOKEN_ENDPOINT.add_path('{uuid}'.format(uuid=uuid))


def sec_get_detail(uuid):
    return METADATA_ENDPOINT.add_path('script-execution-configurations/{uuid}'.format(uuid=uuid))


def sec_get_query_id(uuid):
    return DATA_ENDPOINT.add_path('script-execution-configurations/{uuid}/queries'.format(uuid=uuid))


def performance_get_detail(uuid):
    return EXECUTION_METADATA_ENDPOINT.add_path('v2/performances/{uuid}/'.format(uuid=uuid))


def performance_output_parameter_post(parameter_id, performance_id):
    return EXECUTION_METADATA_ENDPOINT.\
        add_path('v2/performances/{performance_id}/output-parameters/{parameter_id}/value/'.
                 format(performance_id=performance_id, parameter_id=parameter_id))


def logging_post(performance_id):
    return LOGGING_ENDPOINT.add_path('performances/{performance_id}/'.format(performance_id=performance_id))


def matrices_upload(dataset_id, matrices_id):
    return DATA_ENDPOINT.add_path('script-execution-configurations/{sec_id}/'
                                  'datasets/{dataset_id}/matrices/{matrices_id}/upload'.
                                  format(sec_id=Store.config_id, dataset_id=dataset_id, matrices_id=matrices_id))


def matrices_get(dataset_id, matrices_id):
    return DATA_ENDPOINT.add_path('script-execution-configurations/{sec_id}/'
                                  'datasets/{dataset_id}/matrices/{matrices_id}/data'.
                                  format(sec_id=Store.config_id, dataset_id=dataset_id, matrices_id=matrices_id))

def matrices_get_by_sql(query_job_id):
    return DATA_ENDPOINT.add_path('queries/{query_job_id}'.
                                  format(query_job_id=query_job_id))


def sec_matrices_get(sec_id, dataset_id, matrices_id):
    return DATA_ENDPOINT.add_path('script-execution-configurations/{sec_id}/datasets/'
                                  '{dataset_id}/matrices/{matrices_id}/data'.
                                  format(sec_id=sec_id, dataset_id=dataset_id, matrices_id=matrices_id))


def sec_matrices_get_by_sql(query_job_id):
    return DATA_ENDPOINT.add_path('script-execution-configurations/{sec_id}/queries/{query_job_id}'.
                                  format(sec_id=Store.config_id, query_job_id=query_job_id))


def sec_matrices_insert(sec_id, dataset_id, matrices_id):
    return DATA_ENDPOINT.add_path('script-execution-configurations/{sec_id}/datasets/'
                                  '{dataset_id}/matrices/{matrices_id}/insert'.
                                  format(sec_id=sec_id, dataset_id=dataset_id, matrices_id=matrices_id))


def sec_matrices_batch_insert(sec_id, dataset_id, matrices_id):
    return DATA_ENDPOINT.add_path('script-execution-configurations/{sec_id}/datasets/'
                                  '{dataset_id}/matrices/{matrices_id}/upload'.
                                  format(sec_id=sec_id, dataset_id=dataset_id, matrices_id=matrices_id))


def object_download(repo_id, file_id):
    return DATA_ENDPOINT.add_path('blob-repositories/{repo_id}/download'.
                                  format(repo_id=repo_id)).add_query_param('name', file_id)


def object(repo_id, file_id):
    return DATA_ENDPOINT.add_path('blob-repositories/{repo_id}'.
                                  format(repo_id=repo_id)).add_query_param('name', file_id)
