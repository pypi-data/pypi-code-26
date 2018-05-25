import fabric
from fabric import _version, connection, runners, group


class init:
    "__init__"

    def version_and_version_info(self):
        for name in ("__version_info__", "__version__"):
            assert getattr(_version, name) == getattr(fabric, name)

    def Connection(self):
        assert fabric.Connection is connection.Connection

    def Remote(self):
        assert fabric.Remote is runners.Remote

    def Result(self):
        assert fabric.Result is runners.Result

    def Config(self):
        assert fabric.Config is connection.Config

    def Group(self):
        assert fabric.Group is group.Group

    def SerialGroup(self):
        assert fabric.SerialGroup is group.SerialGroup

    def ThreadingGroup(self):
        assert fabric.ThreadingGroup is group.ThreadingGroup

    def GroupResult(self):
        assert fabric.GroupResult is group.GroupResult
