from pathlib import Path
from subprocess import *
from tempfile import *
import re, platform, os, json, sys, argparse, signal, urllib, tarfile, tempfile, glob, subprocess, io
import urllib.request
from .directory.local import LocalDirectory
from .directory.encrypted import EncryptedDirectory

# directory =
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--secret",
        metavar="SECRET",
        nargs="?",
        help="value of %%nyptune_secret in the related notebook",
    )
    parser.add_argument(
        "--cache",
        metavar="PATH",
        nargs="?",
        default=str(Path.home() / ".nyptune"),
        help="an alternative location to ~/.nyptune",
    )
    notebook = {
        "metavar": "NOTEBOOK",
        "type": str,
        "nargs": 1,
        "help": "the path to a nyptune-enabled notebook",
    }
    name = {
        "metavar": "NAME",
        "type": str,
        "nargs": 1,
        "help": "value of %%nyptune_name in the related notebook",
    }
    subparsers = parser.add_subparsers(help="a subcommand")
    init_parser = subparsers.add_parser(
        "init", help="initialize ipfs and add the save hook to the jupyter config file"
    )
    init_parser.set_defaults(func=init)
    add_parser = subparsers.add_parser(
        "add",
        help="Makes nyptune aware of a notebook file you haven't yet opened and saved locally.",
    )
    add_parser.add_argument("notebook", **notebook)
    add_parser.set_defaults(func=add)

    pull_parser = subparsers.add_parser(
        "pull", help="Pulls cached files from ipfs to local storage"
    )
    # pull_parser.add_argument("name", **name)
    pull_parser.set_defaults(func=pull)
    push_parser = subparsers.add_parser(
        "push", help="Pushes cached files from local storage to ipfs"
    )
    # push_parser.add_argument("name", **name)
    push_parser.set_defaults(func=push)
    pin_parser = subparsers.add_parser("pin", help="Makes cached files more permanent")
    pin_parser.set_defaults(func=pin)
    gc_parser = subparsers.add_parser(
        "gc", help="Removes unused files from the local cache"
    )
    gc_parser.set_defaults(func=gc)
    recreate_parser = subparsers.add_parser(
        "recreate", help="Recreate the environment used to create a notebook"
    )
    recreate_parser.set_defaults(func=recreate)
    recreate_parser.add_argument("notebook", **notebook)
    start_parser = subparsers.add_parser("start", help="starts ipfs")
    start_parser.set_defaults(func=start)
    stop_parser = subparsers.add_parser("stop", help="stops ipfs")
    stop_parser.set_defaults(func=stop)
    if len(sys.argv) == 1:
        parser.print_help()
    else:
        parsed = parser.parse_args()
        parsed.func(parsed)


def _dir(parsed_args):
    args = vars(parsed_args)
    d = LocalDirectory(args["cache"])
    if "secret" in args and args["secret"]:
        d = EncryptedDirectory(d, args["secret"])
    return d


def add(parsed_args):
    root = _dir(parsed_args)
    for path in root.glob("*.json"):
        with root.reader(path) as file:
            props = json.load(file)
        for name, details in props.items():
            if not "ipfs" in details:
                proc = subprocess.run(
                    [
                        ipfs(),
                        "add",
                        "--nocopy",
                        str(Path.home() / ".nyptune" / details["checksum"]),
                    ],
                    stdout=subprocess.PIPE,
                )
                result = proc.stdout.decode("utf-8")
                print(result)
                _, sig, _ = result.split()
                details["ipfs"] = sig
        with root.writer(path) as file:
            json.dump(props, io.TextIOWrapper(file))


def push(parsed_args):
    root = _dir(parsed_args)
    for path in root.glob("*.json"):
        with root.reader(path) as file:
            props = json.load(file)
        for name, details in props.items():
            if not "ipfs" in details:
                proc = subprocess.run(
                    [
                        ipfs(),
                        "add",
                        "--nocopy",
                        str(Path.home() / ".nyptune" / details["checksum"]),
                    ],
                    stdout=subprocess.PIPE,
                )
                result = proc.stdout.decode("utf-8")
                print(result)
                _, sig, _ = result.split()
                details["ipfs"] = sig
        with root.writer(path) as file:
            json.dump(props, io.TextIOWrapper(file))


def pull(parsed_args):
    root = _dir(parsed_args)
    for path in root.glob("*.json"):
        with root.reader(path) as file:
            props = json.load(file)
        for name, details in props.items():
            if "ipfs" in details and not root.exists(details["checksum"]):
                proc = subprocess.run(
                    [
                        ipfs(),
                        "get",
                        details["ipfs"],
                        "-o",
                        str(Path(parsed_args.cache) / details["checksum"]),
                    ],
                    stdout=subprocess.PIPE,
                )
                result = proc.stdout.decode("utf-8")
                print(result)


def gc(parsed_args):
    root = _dir(parsed_args)
    checksums = {}
    for path in root.glob("*.json"):
        with root.reader(path) as file:
            props = json.load(file)
        for name, details in props.items():
            checksums[details["checksum"]] = True

    for path in root.glob("*"):
        if (
            not path.startswith("_")
            and not path.endswith(".json")
            and not checksums.get(path)
        ):
            print("no reference to " + path + ", removing...")
            root.remove(path)


def pin(parsed_args):
    print("not implemented")
    pass


def start(parsed_args):
    if not Path(ipfs()).is_file():
        init()
    pid = os.fork()
    if pid == 0:
        os.execl(ipfs(), "ipfs", "daemon")
    else:
        with open(Path(gettempdir()) / "nyptune.pid", "w") as file:
            file.write(str(pid) + "\n")


def stop(parsed_args):
    pid_path = Path(gettempdir()) / "nyptune.pid"
    if pid_path.is_file():
        with open(pid_path) as file:
            pid = file.read()
            os.kill(int(pid), signal.SIGTERM)
            pid_path.unlink()
    else:
        print("Nyptune daemon not running: no pid file found")


def ipfs():
    return str(Path(os.path.realpath(__file__)).parent / "go-ipfs" / "ipfs")


def recreate(parsed_args):
    notebook = parsed_args.notebook[0]
    cache = Path(notebook).parent / ".nyptune"
    with open(notebook) as file:
        model = json.load(file)
        conda = "\n".join(
            [
                line
                for line in model["metadata"]["magix"]["conda"]
                if line != "@EXPLICIT"
            ]
        )
        with NamedTemporaryFile() as conda_env_yaml:
            conda_env_yaml.write(conda.encode("utf-8"))
            conda_env_yaml.flush()
            print(conda_env_yaml.name)
            result = run(
                [
                    "conda",
                    "create",
                    "-y",
                    "--name",
                    sys.argv[1],
                    "--file",
                    conda_env_yaml.name,
                ],
                encoding="utf-8",
                shell=False,
            )
            if result.returncode != 0:
                result = run(
                    [
                        "conda",
                        "env",
                        "update",
                        "-y",
                        "--name",
                        sys.argv[1],
                        "--file",
                        conda_env_yaml.name,
                    ],
                    encoding="utf-8",
                    shell=False,
                )
        sig = model["metadata"]["magix"]["cache"][".nyptune"]
        run([ipfs(), "get", sig, "-o", cache], shell=False)
        with NamedTemporaryFile() as requirements:
            pip = "\n".join(model["metadata"]["magix"]["pip"])
            requirements.write(pip.encode("utf-8"))
            requirements.flush()
            with NamedTemporaryFile() as script:
                s = [
                    "#!/bin/bash",
                    "source activate " + sys.argv[1],
                    "pip install -y -r " + requirements.name,
                    "jupyter notebook",
                ]
                script.write("\n".join(s).encode("utf-8"))
                script.flush()
                os.chmod(script.name, 0o755)
                print("running " + script.name)
                print("\n".join(s))
                os.execl(script.name, "jupyter")


def init(parsed_args):
    config = Path.home() / ".jupyter" / "jupyter_notebook_config.py"
    if not config.is_file():
        print("generating an empty jupyter config file")
        run(["jupyter", "notebook", "--generate-config"], encoding="utf-8", shell=False)
    with open(config, "r") as file:
        contents = file.read()

    if "nyptune" in contents:
        print("jupyter config file already mentions nyptune")
    else:
        with open(config, "a") as file:
            print("appending nyptune pre-save-hook to jupyter config")
            file.write(
                "\nfrom nyptune.jupyter import presave\nc.ContentsManager.pre_save_hook = presave\n"
            )

    if "64" in platform.machine():
        arch = "amd64"
    else:
        arch = "386"
    plat = platform.system().lower()
    version = "0.4.14"
    print("downloading ipfs")
    local = Path(tempfile.gettempdir()) / "go-ipfs.tar.gz"
    urllib.request.urlretrieve(
        f"https://dist.ipfs.io/go-ipfs/v{version}/go-ipfs_v{version}_{plat}-{arch}.tar.gz",
        local,
    )
    with tarfile.open(local, "r|gz") as tar:
        tar.extractall(Path(os.path.realpath(__file__)).parent)
    print("initializing ipfs")
    run([ipfs(), "init"], encoding="utf-8", shell=False)
    run(
        [ipfs(), "config", "--json", "Experimental.FilestoreEnabled", "true"],
        encoding="utf-8",
        shell=False,
    )
