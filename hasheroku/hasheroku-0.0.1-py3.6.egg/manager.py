import os
import os.path as path
import importlib.util

import yaml

# TODO: move error msgs into separate file?
RESULTS_EXIST_ERROR_MSG = ("`{}` directory or file already exists: "
    "have you already run this experiment? "
    "Provide `--overwrite` option if you want to overwrite the results.")

def start_experiment(args):
    experiments_dir = "./experiments"
    exp_name = args.name # Name of the experiment is the same as config name

    config_path = path.join(experiments_dir, exp_name, "config.yml")
    logs_path = path.join(experiments_dir, exp_name, "logs")
    summary_path = path.join(experiments_dir, exp_name, "summary.md")

    if not path.isfile(config_path): raise FileNotFoundError(config_path)
    if os.listdir(logs_path) != []: raise Exception(RESULTS_EXIST_ERROR_MSG.format(logs_path))
    if os.path.isfile(summary_path): raise Exception(RESULTS_EXIST_ERROR_MSG.format(summary_path))

    os.mkdir(logs_path)

    with open(config_path, "r", encoding="utf-8") as config_file:
        config = yaml.safe_load(config_file)

    # TODO: validate config

    # runner_path = path.join("src/runners/", config.get("runner") + ".py")
    # runner_module_name = "module.runner." + config.get("runner") # TODO: can be arbitrary? Can we have name collisions?
    # runner_module_spec = importlib.util.spec_from_file_location(runner_module_name, runner_path)
    # runner = importlib.util.module_from_spec(runner_module_spec)
    # runner_module_spec.loader.exec_module(runner)
    runners = importlib.import_module('src.runners')
    runner_cls = getattr(runners, config.get('runner'))
    runner = runner_cls(config)
    runner.start()
