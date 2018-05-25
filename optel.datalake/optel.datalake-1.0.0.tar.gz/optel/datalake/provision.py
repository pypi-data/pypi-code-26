from python_terraform import Terraform
import os

provision_dir = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), "provision")


def create_machines(config):
    """Create and provision machines with terraform

    Args:
        config (str): Terraform configuration dir. The
                    directory is used to store the config
                    file as well as Terraform specific stuff.
                    .. note::

                        Each directory has to be cloud provider specific.
    """
    kwargs = {"auto-approve": True}
    config_dir = os.path.join(provision_dir, config)
    tf = Terraform(working_dir=config_dir)
    tf.init()
    tf.apply(config_dir, capture_output=False, **kwargs)


def destroy_machines(config):
    """Destroy machines with terraform.

    Args:
        config(str): Terraform configuration dir to use.
    """
    kwargs = {"auto-approve": True}
    config_dir = os.path.join(provision_dir, config)
    tf = Terraform(working_dir=config_dir)
    tf.destroy(capture_output=False, **kwargs)
