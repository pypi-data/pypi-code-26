# apydoc.init: initialize a package for use with apydoc

import sys, os, json

if __name__ == "__main__":
    path = os.path.realpath(sys.argv[1])
    j = {"srcs": ["."], "docs": "docs"}
    if not os.path.exists(j["docs"]):
        os.makedirs(j["docs"])
    apydoc_json_fn = os.path.join(path, "apydoc.json")
    with open(apydoc_json_fn, "wb") as f:
        f.write(json.dumps(j, indent=2).encode("utf-8"))
    print("wrote %s" % apydoc_json_fn)
