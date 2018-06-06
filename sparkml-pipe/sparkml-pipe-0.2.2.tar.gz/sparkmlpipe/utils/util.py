import yaml
import os
import uuid
from pyspark.ml import Pipeline

from .constants import APP_PATH


def random_uid(name):
    """
    Generate a unique unicode id for the object. The default implementation
    concatenates the class name, "_", and 12 random hex chars.
    """
    return str(name + "_" + uuid.uuid4().hex[12:])


def load_config(conf_path):
    with open(conf_path, 'r') as f:
        config = yaml.load(f)

    return config


def load_stage_conf_list(main_conf, stage_conf_dir):
    stage_ids = main_conf['stages']
    stage_conf_list = []
    for index, stage_id in enumerate(stage_ids):
        stage_path = get_stage_path(stage_id, index, len(stage_ids), stage_conf_dir)
        stage_conf = load_config(stage_path)
        stage_conf_list.append(stage_conf)
    return stage_conf_list


def save_instance_configs(main_conf, stage_conf_list):
    conf_dir = os.path.join(APP_PATH, 'conf', main_conf['uid'])

    os.makedirs(conf_dir, exist_ok=True)

    with open(os.path.join(conf_dir, 'main.yaml'), 'w') as outfile:
        yaml.dump(main_conf, outfile, default_flow_style=False)

    stage_conf_dir = os.path.join(conf_dir, 'stages')
    os.makedirs(stage_conf_dir, exist_ok=True)

    for stage_conf in stage_conf_list:
        with open(os.path.join(stage_conf_dir, stage_conf['uid'] + '.yaml'), 'w') as outfile:
            yaml.dump(stage_conf, outfile, default_flow_style=False)

def get_class(clazz):
    """
    Loads Python class from its name.
    """
    parts = clazz.split('.')
    module = ".".join(parts[:-1])
    m = __import__(module)
    for comp in parts[1:]:
        m = getattr(m, comp)
    return m


def get_stage_path(stage_id, stage_idx, num_stages, stages_dir):
    """
    Get path for the given handler.
    """
    stage_idx_digits = len(str(num_stages))
    stage_dir = str(stage_idx).zfill(stage_idx_digits) + "_" + stage_id + '.yaml'
    stage_path = os.path.join(stages_dir, stage_dir)
    return stage_path


class PipelineLoader:
    """
    Class for loading stages from the main.yaml and the related handler configs
    """
    @staticmethod
    def load(main_conf, stage_conf_list):
        """
        Load metadata and stages for a :py:class:`Pipeline` or :py:class:`PipelineModel`
        :return: (UID, list of stages)
        """
        stages = []
        for stage_conf in stage_conf_list:
            stage = StageLoader.load(stage_conf)
            stages.append(stage)

        mlpipe = Pipeline(stages=stages)
        mlpipe._resetUid(main_conf['uid'])

        return mlpipe


class StageLoader:
    """
    Class for stages that contain basic yaml format params.
    """
    @staticmethod
    def load(conf):
        py_type = get_class(conf['class'])
        instance = py_type()
        if 'uid' in conf:
            instance._resetUid(conf['uid'])
        StageLoader.get_set_params(instance, conf)
        return instance

    @staticmethod
    def get_set_params(instance, conf):
        """
        Extract Params from metadata, and set them in the instance.
        """
        # Set user-supplied param values
        for paramName in conf['paramMap']:
            param = instance.getParam(paramName)
            paramValue = conf['paramMap'][paramName]
            instance.set(param, paramValue)
