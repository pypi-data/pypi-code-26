from subprocess import *
from pathlib import Path
import os, json


def presave(path, model, contents_manager):
    if model["type"] == "notebook":
        namespace = "default"
        for cell in model["content"]["cells"]:
            lines = cell["source"].split("\n")
            for line in lines:
                if line.startswith("%nyptune_name") or line.startswith(
                    "%%nyptune_name"
                ):
                    namespace = line.split()[1]
        path = Path.home() / ".nyptune" / (namespace + ".metadata.json")

        nyptune = model["content"]["metadata"]["nyptune"] = {}
        if path.is_file():
            with open(path, "r") as file:
                model["content"]["metadata"]["nyptune"]["cache"] = json.load(file)
        conda = run(
            ["conda", "list", "--explicit"], stdout=PIPE, encoding="utf-8", shell=False
        )
        nyptune["conda"] = conda.stdout.split("\n")
        pip = run(
            ["pip", "list", "--format", "freeze"],
            stdout=PIPE,
            encoding="utf-8",
            shell=False,
        )
        nyptune["pip"] = pip.stdout.split("\n")
