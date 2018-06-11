"""Test Conan promote features

"""

import pytest
from conans.test.utils.tools import TestServer, TestClient
from conans.client import conan_api
from conan import conan_promote

CONANFILE = """from conans import ConanFile
class MyPkg(ConanFile):
    name = "Hello"
    version = "0.1.0"
    exports_sources = "*"
    def package(self):
        self.copy("*")
"""


@pytest.fixture
def setup():
    test_server = TestServer(
        read_permissions=[("*/*@*/*", "*")],
        write_permissions=[("*/*@*/*", "conanuser")],
        users={"conanuser": "conanpass"})
    client = TestClient(
        servers={"testing": test_server},
        users={"testing": [("conanuser", "conanpass")]})
    client.save({"conanfile.py": CONANFILE})
    return (test_server, client)


def test_promote_run(setup):
    """Default Conan Promote flow

    :return:
    """
    test_server, client = setup
    client.run("create . conanuser/testing")
    client.run("upload Hello/0.1.0@conanuser/testing --confirm --all")
    client.run("search -r testing")
    assert "Hello/0.1.0@conanuser/testing" in client.user_io.out
    assert "Hello/0.1.0@conanuser/stable" not in client.user_io.out

    client.run("remove Hello/0.1.0@conanuser/testing --force")
    client.run("search")
    assert "There are no packages" in client.user_io.out

    promote = conan_promote.ConanPromote()
    promote.conan_instance = conan_api.Conan(client.client_cache,
                                             client.user_io, client.runner,
                                             client.remote_manager, None)
    promote.run([
        "Hello/0.1.0@conanuser/testing", "-r", "testing", "-s", "testing",
        "-u", "conanuser"
    ])

    client.run("search -r testing")
    assert "Hello/0.1.0@conanuser/testing" in client.user_io.out
    assert "Hello/0.1.0@conanuser/stable" in client.user_io.out
    client.run("search")
    assert "There are no packages" in client.user_io.out
