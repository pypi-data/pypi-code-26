#!/usr/bin/env python

import json
import os
import logging
import subprocess
import sys
from time import sleep

import yaml
from shutil import copyfile

workdir = os.environ.get('LOOPER_WORKDIR', os.path.join(os.environ['HOME'], '.benchmark-looper'))
compose_path = os.environ.get("LOOPER_COMPOSE_FILE", "/etc/benchmark-looper/docker-compose.yml")

todo_path = os.path.join(workdir, 'todo.json')
done_path = os.path.join(workdir, 'done.json')
error_path = os.path.join(workdir, 'error.json')
custom_compose_path = os.path.join(workdir, 'custom-compose.yml')

root = logging.getLogger()
root.setLevel(logging.DEBUG)
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
root.addHandler(ch)


def todo_peek():
    with open(todo_path, 'r') as f:
        data = json.loads(f.read())
        return data[0]


def todo_pop():
    with open(todo_path, 'r+') as f:
        data = json.loads(f.read())
        f.seek(0)
        f.truncate()
        f.write(json.dumps(data[1:]))
        return data[0]


def append(path, job):
    logging.info("appending to " + path)
    mode = 'r+' if os.path.exists(path) else 'a+'
    with open(path, mode) as f:
        content = f.read()
        logging.info("reading content of {}: {}".format(path, content))
        if len(content) == 0:
            content = "[]"
        data = json.loads(content)
        data.append(job)
        f.seek(0)
        f.truncate()
        logging.info("writing data {} to {}".format(data, path))
        f.write(json.dumps(data))
        f.close()


def done_append(job):
    append(done_path, job)


def error_append(job):
    append(error_path, job)


def iter_jobs():
    while True:
        try:
            yield todo_peek()
        except IndexError:
            return


def generate_custom_compose_file(base_compose_data, job):
    custom_compose_data = base_compose_data.copy()

    for name, value in job.items():
        custom_compose_data['services']['main']['environment'][name] = value

    logging.info("generating custom compose file {}".format(custom_compose_data))

    with open(custom_compose_path, 'w+') as f:
        yaml.dump(custom_compose_data, f)


def get_job_status():
    status = subprocess.check_output(["bash", "-c", "docker service ps bench_main  | tail -n 1 | awk '{ print $5 }'"])
    logging.info("current status is '{}'".format(status))
    return status.strip()


def execute_job(job, base_compose_data):
    logging.info("executing job")

    generate_custom_compose_file(base_compose_data, job)
    logging.info(subprocess.check_output("docker stack deploy -c {} bench".format(custom_compose_path).split()))

    sleep(1)

    status = get_job_status()
    while status == "Running":
        sleep(1)
        status = get_job_status()

    logging.info(subprocess.check_output("docker stack rm bench".split()))

    # start service
    # wait service shutdown
    return status == "Shutdown"


def parse_compose_file(path):
    with open(path, 'r') as f:
        compose_data = yaml.load(f)
    return compose_data


def setup(user_todo_path):
    if not os.path.exists(workdir):
        os.mkdir(workdir)

    if not os.path.exists(user_todo_path):
        logging.error("todo file {} does not exists".format(user_todo_path))
        exit(1)

    with open(user_todo_path, 'r') as f:
        data = json.load(f)
        if data.__class__ != list:
            logging.error('todo file is not a valid json array')
            exit(1)

    logging.info("copying todo file")
    copyfile(user_todo_path, todo_path)


def main():
    logging.info("todo path = " + todo_path)
    logging.info("done path = " + done_path)
    logging.info("error path = " + error_path)

    compose_data = parse_compose_file(compose_path)

    for job in iter_jobs():
        logging.info("processing job " + json.dumps(job))
        success = execute_job(job, compose_data)
        todo_pop()
        if success:
            logging.info("last job succeed")
            done_append(job)
        else:
            logging.warning("last job failed")
            error_append(job)

if __name__ == '__main__':

    if len(sys.argv) != 2:
        print("usage: benchmark-looper.py todo.json")
        exit(1)

    setup(sys.argv[1])
    main()
