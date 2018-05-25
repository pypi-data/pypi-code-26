import os


class NotVersionControlledOSReleaseException(Exception):
    pass


class DeviceInformation:
    DEVICE_TREE_PREFIX_PATH = "/proc/device-tree/hat/"
    vendor_path = DEVICE_TREE_PREFIX_PATH + "vendor"
    product_path = DEVICE_TREE_PREFIX_PATH + "product"
    issue_path = "/boot/issue.txt"
    edge_path = "/edge"

    def __init__(self):
        if not (self.try_to_detect_navio() or self.try_to_detect_edge()):
            self._product = 'Seems like you booted without Navio properly screwed!'
            self._vendor = '¯\_(ツ)_/¯ Unknown, but most likely Emlid'

        try:
            with open(self.issue_path, 'r') as f:
                self._issue = " ".join(f.read().split()[:3])
        except IOError:
            raise NotVersionControlledOSReleaseException("Seems like you're using the old image. Consider reflashing!")

        self._kernel = self._set_kernel()

    def try_to_detect_navio(self):
        try:
            with open(self.vendor_path, 'r') as f:
                self._vendor = f.read().strip('\x00 ').strip()

            with open(self.product_path, 'r') as f:
                self._product = f.read().strip('\x00 ').strip()
            return True
        except IOError:
            return False

    def try_to_detect_edge(self):
        if os.path.exists(self.edge_path):
            self._product = "Edge"
            self._vendor = "Emlid Limited"
            return True
        else:
            return False

    def __repr__(self):
        info = ("Vendor: {_vendor}\n"
                "Product: {_product}\n"
                "Issue: {_issue}\n"
                "Kernel: {_kernel}").format(**dict(vars(self).items()))
        return info

    @property
    def vendor(self):
        return self._vendor

    @property
    def product(self):
        return self._product

    @property
    def issue(self):
        return self._issue

    @property
    def kernel(self):
        return self._kernel

    @staticmethod
    def _set_kernel():
        return os.uname()[2]
