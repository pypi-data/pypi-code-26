import re
from helga import log
from txproductpages import milestones


logger = log.getLogger(__name__)


class ReleaseTask(object):
    """ Normalize a release task into a value PP understands. """
    def __init__(self, product, version, milestone):
        self.product = product
        self.version = version
        self.milestone = milestone

    @property
    def shortname(self):
        """
        Return a release's shortname according to PP.
        """
        return '%s-%s' % (self.product, self.version)

    @property
    def task_re(self):
        """
        Return a regex that will match this task in PP's tasks list.
        """
        if self.milestone == 'ga':
            return milestones.GA
        if self.milestone == 'dev freeze':
            return milestones.DEV_FREEZE
        # Some product-specific things:
        if self.product == 'ceph' and re.match('z\d+', self.milestone):
            return re.compile(r'.*%s GA' % self.milestone, flags=re.IGNORECASE)
        if self.product == 'rhosp' and self.milestone == 'beta':
            return re.compile(r'.*Public Beta', flags=re.IGNORECASE)
        # Fallback to just searching for this text
        return re.compile('.*%s' % self.milestone, flags=re.IGNORECASE)

    @classmethod
    def from_text(klass, text):
        """
        Transform some common name patterns into values that PP understands.

        Humans describe releases in a variety of ways. Let's try to match them.
        :param text: "RHEL 7" or "OSP 13 Beta"
        :returns: ReleaseTask, or None if we it did not look like a valid
                  release.
        """
        text = text.lower()
        (product, version, milestone) = ReleaseTask.split(text)
        product = ReleaseTask.canonical_product(product)
        version = ReleaseTask.canonical_version(product, version)
        milestone = ReleaseTask.canonical_milestone(product, milestone)
        if product is None or version is None or milestone is None:
            return None
        return klass(product, version, milestone)

    @staticmethod
    def split(text):
        """ Split a user's release text into product, version, milestone. """
        text = text.replace('-', ' ')
        try:
            parts = text.split(' ', 2)
        except ValueError:
            return (None, None, None)
        if len(parts) == 2:
            (product, version) = parts
            milestone = 'ga'
        elif len(parts) == 3:
            (product, version, milestone) = parts
        else:
            # Not possible?
            err = "couldn't parse product/version/milestone from %s"
            logger.debug(err % text)
            return (None, None, None)
        # Maybe the user specified a version and milestone smashed together,
        # like "3.0z2". Split that out into the milestone field.
        if 'z' in version:
            index = version.find('z')
            milestone = version[index:]
            version = version[:index]
        return (product, version, milestone)

    @staticmethod
    def canonical_product(product):
        """ Canonicalize some common ways to reference a product. """
        product_patterns = (
          (r'^cfme', 'cloudforms'),
          (r'^cf', 'cloudforms'),
          (r'^rhceph', 'ceph'),
          (r'^rh ceph', 'ceph'),
          (r'^rhcs', 'ceph'),
          (r'^manageiq', 'cloudforms'),
          (r'^osp', 'rhosp'),
        )
        for (pattern, normalized) in product_patterns:
            product = re.sub(pattern, normalized, product)
        return product

    @staticmethod
    def canonical_version(product, version):
        """ Canonicalize some common ways to reference a product's version. """
        # Ceph, Cloudforms, and RHEL versions are of the form "3-0"
        if product in ('ceph', 'cloudforms', 'rhel'):
            version = version.replace('.', '-', 1)
            # If the user said eg. "RHCS 3", normalize version to "3-0"
            if '-' not in version:
                version += '-0'
        # OSP versions are of the form "13.0"
        if product == 'rhosp':
            if '-' in version:
                version = version.replace('-', '.')
            if '.' not in version and '-' not in version:
                version += '.0'
        return version

    @staticmethod
    def canonical_milestone(product, milestone):
        if milestone == 'release':
            return 'ga'
        return milestone

    def __eq__(self, other):
        if self.product != other.product:
            return False
        if self.version != other.version:
            return False
        if self.milestone != other.milestone:
            return False
        return True

    def __repr__(self):
        tmpl = 'ReleaseTask(product="%s", version="%s", milestone="%s")'
        return tmpl % (self.product, self.version, self.milestone)
