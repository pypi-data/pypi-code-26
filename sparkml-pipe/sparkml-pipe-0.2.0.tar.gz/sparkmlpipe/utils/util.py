import yaml
import os
import uuid
from pyspark.ml import Pipeline


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


def get_stage_sid(stage_id, stage_idx, num_stages):
    """
    Get stage id
    """
    stage_idx_digits = len(str(num_stages))
    return str(stage_idx).zfill(stage_idx_digits) + "_" + stage_id


def get_stage_path(stage_sid, stages_dir):
    """
    Get stage path
    """
    stage_base_path = stage_sid + '.yaml'
    stage_path = os.path.join(stages_dir, stage_base_path)
    return stage_path


class PipelineReader:
    """
    Class for loading pipeline as a spark pipeline object
    """
    @staticmethod
    def load(conf_dir):
        main_conf_path = os.path.join(conf_dir, "main.yaml")
        main_conf = load_config(main_conf_path)
        stages = PipelineConfigReader.load(main_conf, conf_dir)
        return Pipeline(stages=stages)


class PipelineConfigReader:
    """
    Class for loading stages from the main.yaml and the related handler configs
    """
    @staticmethod
    def load(conf, path):
        """
        Load metadata and stages for a :py:class:`Pipeline` or :py:class:`PipelineModel`
        :return: (UID, list of stages)
        """
        stage_dir = os.path.join(path, "stages")
        stage_ids = conf['stages']
        stages = []
        for index, stage_id in enumerate(stage_ids):
            stage_path = PipelineConfigReader.get_stage_path(stage_id, index, len(stage_ids), stage_dir)
            stage_conf = load_config(stage_path)
            stage = StageConfigReader.load(stage_conf)
            stages.append(stage)
        return stages

    @staticmethod
    def get_stage_path(stage_id, stage_idx, num_stages, stages_dir):
        """
        Get path for the given handler.
        """
        stage_idx_digits = len(str(num_stages))
        stage_dir = str(stage_idx).zfill(stage_idx_digits) + "_" + stage_id + '.yaml'
        stage_path = os.path.join(stages_dir, stage_dir)
        return stage_path


class StageConfigReader:
    """
    Class for stages that contain basic yaml format params.
    """
    @staticmethod
    def load(conf):
        py_type = get_class(conf['class'])
        instance = py_type()
        if 'uid' in conf:
            instance._resetUid(conf['uid'])
        StageConfigReader.get_set_params(instance, conf)
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
