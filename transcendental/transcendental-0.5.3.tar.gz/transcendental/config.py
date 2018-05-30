import os
PATH = os.getenv("VIRTUAL_ENV", None)
MODELS = os.path.join("/etc", "transcendental", "models")
if PATH:
    MODELS = os.path.join(PATH, "etc", "transcendental", "models")
