from d3m.metadata import base as meta_base

D3M_API_VERSION = '2018.6.5'
VERSION = '0.3.1'
TAG_NAME = ''

REPOSITORY = 'https://gitlab.datadrivendiscovery.org/dhartnett/psl'
PACAKGE_NAME = 'pslgraph'

# D3M_PERFORMER_TEAM = 'SRI-UCSC'
D3M_PERFORMER_TEAM = 'SRI'

PACKAGE_URI = ''
if TAG_NAME:
    PACKAGE_URI = "git+%s@%s" % (REPOSITORY, TAG_NAME)
else:
    PACKAGE_URI = "git+%s" % (REPOSITORY)

PACKAGE_URI = "%s#egg=%s" % (PACKAGE_URI, PACAKGE_NAME)

INSTALLATION = {
    'type' : meta_base.PrimitiveInstallationType.PIP,
    'package': PACAKGE_NAME,
    'version': VERSION
}

INSTALLATION_JAVA = {
    'type' : meta_base.PrimitiveInstallationType.UBUNTU,
    'package': 'default-jre',
    'version': '2:1.8-56ubuntu2'
}

INSTALLATION_POSTGRES = {
    'type' : meta_base.PrimitiveInstallationType.UBUNTU,
    'package': 'postgresql',
    'version': '9.5+173ubuntu0.1'
}
