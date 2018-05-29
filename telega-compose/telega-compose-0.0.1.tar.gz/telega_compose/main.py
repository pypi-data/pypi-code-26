#!/usr/bin/env python

import argparse
import os
import sys

from subprocess import Popen, PIPE, STDOUT

from yaml import load, dump

try:
    from yaml import CLoader as Loader, CSafeDumper as SafeDumper
except ImportError:
    from yaml import Loader, SafeDumper


def render_state(state: str, yml_filename: str) -> str:
    assert os.path.exists(yml_filename), "States file {filename} not found.".format(filename=yml_filename)

    with open(yml_filename, 'r') as yml_file:
        yml = load(yml_file.read(), Loader=Loader)

    states = yml.get('states')
    assert states, "Section 'states' must contain at least one state."

    state_yml = states.get(state)
    assert state_yml, "Unknown state {state}. Available states are: {available_states}.".format(
        state=state, available_states=', '.join(sorted(states.keys()))
    )

    compose_yml = yml.get('compose', {})
    compose_yml.update(state_yml)

    dumper = SafeDumper
    dumper.ignore_aliases = lambda self, data: True  # Do not use YAML aliases - generate redundant YAML
    rendered = dump(compose_yml, Dumper=dumper, default_flow_style=False)

    return rendered


def parse_cli_args() -> tuple:
    usage_text = """example:

     {app_file} local config
     {app_file} live -f /path/to/states.yml up -d
     {app_file} qa -f /path/to/states.yml --project-name acme up""".format(app_file=sys.argv[0])

    parser = argparse.ArgumentParser(
        description="generate docker-compose file for concrete state",
        epilog=usage_text,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('state', help="state to render docker-compose file")
    parser.add_argument('-f', '--file', help="states file, by default: states.yml")
    return parser.parse_known_args()


def cli() -> None:

    # Render state
    args, compose_args = parse_cli_args()
    if args.file is None:
        filename = os.path.join(os.getcwd(), 'states.yml')
    else:
        filename = args.file
    state = render_state(args.state, filename)

    # Run docker-compose with rendered state
    compose_args = ['docker-compose', '-f', '-'] + compose_args
    compose_process = Popen(compose_args, stdout=PIPE, stdin=PIPE, stderr=STDOUT, universal_newlines=True)
    compose_process.stdin.write(state)
    compose_process.stdin.close()

    # Print docker-compose output
    while not compose_process.poll():
        try:
            line = compose_process.stdout.readline()
            if line:
                sys.stdout.write(line)
            else:
                break
        except KeyboardInterrupt:
            compose_process.terminate()
            compose_process.wait()  # Wait for closing docker-compose gracefully


if __name__ == '__main__':
    cli()
