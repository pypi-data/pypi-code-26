import os
import shutil
from .link import Link
from .utils import PROFILE_NAME, GENERIC_DIR, FORCE
from .profile import Profile


class Target:
    def __init__(self, base, hostname, username):
        self.base = base
        self.hostname = hostname
        self.username = username
        self.target_home = os.path.join(self.base, self.hostname, self.username)
        self.profile = self._get_profile(PROFILE_NAME)

    def _get_profile(self, profile_name: str):
        profile_file = os.path.join(self.target_home, profile_name)
        profile = Profile()
        profile.read_from_yaml(profile_file)
        return profile

    def get_bundle_home(self, bundle):
        if bundle.get('generic'):
            bundle_home = os.path.join(self.base, GENERIC_DIR, bundle['name'])
        else:
            bundle_home = os.path.join(self.target_home, bundle['name'])

        if not os.path.exists(bundle_home):
            os.makedirs(bundle_home)
        return bundle_home

    @staticmethod
    def get_link_names(bundle: dict):
        link_names = []
        for link in bundle['links']:
            link_names.append(link['src'])
        return link_names

    def get_bundle_names(self):
        bundle_names = []
        for bundle in self.profile.bundles:
            bundle_names.append(bundle.name)
        return bundle_names

    def deploy_bundle(self, bundle: dict, force=FORCE):
        status = dict()
        bundle_home = self.get_bundle_home(bundle)

        for link in bundle['links']:
            link = Link(bundle_home, link)
            s, e = link.src_to_dst(force=force)
            status[link.name] = (s, e)
        return status

    def collect_bundle(self, bundle: dict, force=FORCE):
        status = dict()
        bundle_home = self.get_bundle_home(bundle)

        for link in bundle['links']:
            link = Link(bundle_home, link)
            s, e = link.dst_to_src(force=force)
            status[link.name] = (s, e)
            return status

    def deploy_all(self, force=FORCE):
        for bundle in self.profile.bundles.values():
            self.collect_bundle(bundle, force=force)

    def collect_all(self, force=FORCE):
        for bundle in self.profile.bundles:
            self.collect_bundle(bundle, force=force)
