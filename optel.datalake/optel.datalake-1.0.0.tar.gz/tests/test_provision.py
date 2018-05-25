from optel.datalake import provision
import googleapiclient.discovery
import pytest


@pytest.mark.skip(reason="We do not want to test this on every push")
def test_create_machines():
    compute = googleapiclient.discovery.build('compute', 'v1')
    tf_config = "test_gc"
    project = "optel-data-lab"
    zone = "us-east1-d"
    instance = "test-terraform"
    provision.create_machines(tf_config)
    request = compute.instances().get(
        project=project, zone=zone, instance=instance)
    assert request.execute()
    provision.destroy_machines(tf_config)
