"""Script to promote internal Conan package user Conan server
"""

import argparse
import logging
import re
from conan import __version__ as promote_version
from conans.client import conan_api
from conans.errors import ConanException
from conans.model.ref import ConanFileReference

logging.basicConfig(
    format='[%(asctime)s] %(levelname)s: %(message)s', level=logging.WARNING)


class ConanPromote(object):
    """Promote any Conan package to Conan center - stable channel

    """

    def __init__(self):
        self.conan_instance, _, _ = conan_api.Conan.factory()

    @staticmethod
    def _parse_args(*args):
        parser = argparse.ArgumentParser(
            description="Promote Conan package to stable channel")
        parser.add_argument(
            "reference",
            nargs='?',
            help='Reference name to be promoted, e.g: "OpenSSL/1.0.2@user/ci"',
            default=None)
        parser.add_argument(
            "-c", "--channel", help='Stable channel name', default="stable")
        parser.add_argument(
            "-l",
            "--login-user",
            help='Username login to push on stable channel')
        parser.add_argument(
            "-u",
            "--user",
            help='Username to be applied on package name',
            default="user")
        parser.add_argument(
            "-r", "--remote", help='Remote server name', default="bintray")
        parser.add_argument(
            "-V",
            "--verbose",
            help='Enable verbose message',
            action='store_true')
        parser.add_argument(
            "-v", "--version", help='Show version', action='store_true')
        parser.add_argument(
            "-s",
            "--source",
            help='Download the package from this remote',
            default="conan-center")
        return parser.parse_args(*args)

    def _check_arguments(self, parsed_arguments):
        if parsed_arguments.version:
            print("Conan promote version: %s" % promote_version)
            exit(0)

        if not parsed_arguments.reference:
            ConanPromote._fail(
                "Invalid argument. Reference name can not be empty.")

        if parsed_arguments.verbose:
            logging.getLogger().setLevel(logging.DEBUG)

        source_is_valid = False
        target_is_valid = False
        for remote in self.conan_instance.remote_list():
            if remote.name == parsed_arguments.remote:
                target_is_valid = True
            if remote.name == parsed_arguments.source:
                source_is_valid = True
            if target_is_valid and source_is_valid:
                break

        if not target_is_valid:
            ConanPromote._fail(
                "Invalid remote. The remote `%s` is not in your remote list." %
                parsed_arguments.remote)
        if not source_is_valid:
            ConanPromote._fail(
                "Invalid source. The remote `%s` is not in your remote list." %
                parsed_arguments.source)

    @staticmethod
    def _fail(msg):
        logging.error(msg)
        exit(1)

    @staticmethod
    def _stable_reference(parsed_arguments):
        pattern = r"(.*\/.*)@.*\/.*"
        match = re.match(pattern, parsed_arguments.reference)
        if not match:
            ConanPromote._fail("Invalid pattern reference")
        return "%s@%s/%s" % (match.group(1), parsed_arguments.user,
                             parsed_arguments.channel)

    def _clean_local(self, arguments):
        """Clean local package copy after to upload
        """
        self.conan_instance.remove(pattern=arguments.reference, force=True)
        self.conan_instance.remove(
            pattern=ConanPromote._stable_reference(arguments), force=True)

    def run(self, *args):
        """Execute Conan Promote command

        :param args: Input user arguments
        :return:
        """
        parsed_args = ConanPromote._parse_args(*args)
        self._check_arguments(parsed_args)
        try:
            if parsed_args.login_user:
                self.conan_instance.user(
                    remote=parsed_args.remote, name=parsed_args.login_user)
            self._clean_local(parsed_args)
            self.conan_instance.download(
                reference=str(ConanFileReference.loads(parsed_args.reference)),
                remote=parsed_args.source)
            self.conan_instance.copy(
                reference=parsed_args.reference,
                packages=True,
                force=True,
                user_channel="%s/%s" % (parsed_args.user, parsed_args.channel))
            self.conan_instance.upload(
                pattern=ConanPromote._stable_reference(parsed_args),
                all_packages=True,
                force=True,
                remote=parsed_args.remote)
        except ConanException as error:
            self._fail(error.args[0])
        finally:
            self._clean_local(parsed_args)
