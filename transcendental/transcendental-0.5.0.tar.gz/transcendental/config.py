import os
PATH = os.getenv("VIRTUAL_ENV", os.path.join("/etc", "transcendental"))
MODELS = os.path.join(PATH, "etc", "transcendental", "models")
