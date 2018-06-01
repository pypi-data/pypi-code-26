# apydoc.gen: generate apydocs

import json, os, sys
from glob import glob

if __name__ == "__main__":
    path = os.path.realpath(sys.argv[1])
    apydoc_json_fn = os.path.join(path, "apydoc.json")
    if not os.path.exists(apydoc_json_fn):
        apydoc_json_fn = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "apydoc.json.TEMPLATE"
        )
    with open(apydoc_json_fn, "rb") as f:
        j = json.loads(f.read())
    pys = []
    for src in j["srcs"]:
        src_path = os.path.realpath(os.path.join(path, src))
        pys += glob(os.path.join(src_path, "**", "*.py"))
    for py in pys:
        print(py)
