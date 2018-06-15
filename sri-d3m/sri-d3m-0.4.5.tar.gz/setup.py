import setuptools

from sri.common import config

setuptools.setup(
    name = config.PACKAGE_NAME,

    version = config.VERSION,

    description = 'Graph and PSL based TA1 primitive for D3M',
    long_description = 'Graph and PSL based TA1 primitive for D3M',
    keywords = 'd3m_primitive',

    maintainer_email = 'eaugusti@ucsc.edu',
    maintainer = 'Eriq Augustine',

    # The project's main homepage.
    url = config.REPOSITORY,

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers = [
        'Programming Language :: Python :: 3.6',
    ],

    # packages = setuptools.find_packages(exclude = ['contrib', 'docs', 'tests']),
    packages = [
        'sri',
        'sri.autoflow',
        'sri.baseline',
        'sri.common',
        'sri.graph',
        'sri.pipelines',
        'sri.psl',
        'sri.psl.cli',
        'sri.tpot',
    ],

    include_package_data = True,
    package_data = {
        'sri.psl.cli': [
            'psl-cli-CANARY-2.1.1.jar',
            'link_prediction.data',
            'link_prediction.psl'
        ]
    },

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires = [
        # Base
        'd3m', 'networkx', 'pandas>=0.20.1', 'psutil', 'sklearn',
        # TPOT
        'numpy', 'pathos', 'SRITPOT',
        # Testing
        'sripipeline',
    ],

    python_requires = '>=3.6',

    entry_points = {
        'd3m.primitives': [
            # TODO(eriq): Remove once the fix is included in the main D3M release.
            'sri.autoflow = workaround_ignore_error',
            'sri.baseline = workaround_ignore_error',
            'sri.graph = workaround_ignore_error',
            'sri.psl = workaround_ignore_error',
            'sri.tpot = workaround_ignore_error',

            'sri.autoflow.Conditioner = sri.autoflow.conditioner:Conditioner',
            'sri.baseline.MeanBaseline = sri.baseline.mean:MeanBaseline',
            'sri.graph.CollaborativeFilteringParser = sri.graph.collaborative_filtering:CollaborativeFilteringParser',
            'sri.graph.GraphMatchingParser = sri.graph.graph_matching:GraphMatchingParser',
            'sri.graph.GraphTransformer = sri.graph.transform:GraphTransformer',
            'sri.psl.CollaborativeFilteringLinkPrediction = sri.psl.collaborative_filtering_link_prediction:CollaborativeFilteringLinkPrediction',
            'sri.psl.GraphMatchingLinkPrediction = sri.psl.graph_matching_link_prediction:GraphMatchingLinkPrediction',
            'sri.psl.LinkPrediction = sri.psl.link_prediction:LinkPrediction',
            'sri.tpot.StackingOperator = sri.tpot.stacking:StackingOperator',
            'sri.tpot.ZeroCount = sri.tpot.zerocount:ZeroCount',
        ]
    }
)
