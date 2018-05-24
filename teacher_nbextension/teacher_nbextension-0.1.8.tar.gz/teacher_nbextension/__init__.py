from .handlers import load_jupyter_server_extension

# Jupyter Extension points
def _jupyter_nbextension_paths():
    return [dict(
        section="notebook",
        # the path is relative to the `my_fancy_module` directory
        src="static",
        # directory in the `nbextension/` namespace
        dest="teacher_nbextension",
        # _also_ in the `nbextension/` namespace
        require="teacher_nbextension/main")]

def _jupyter_server_extension_paths():
    '''API for server extension installation on notebook 4.2'''
    return [{
        "module": "teacher_nbextension"
}]
