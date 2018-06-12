import os
import typing

from d3m import container
from d3m.metadata import base as meta_base
from d3m.metadata import hyperparams as meta_hyperparams
from d3m.metadata import params as meta_params
from d3m.primitive_interfaces import base as pi_base
from d3m.primitive_interfaces import supervised_learning as pi_supervised_learning

from . import config
from .constants import *
from .networkx import Graph
from .util import get_logger
from .util import set_logging_level
from .psl import build_output_graph
from .psl import run_model
from .psl import write_psl_data

# We can take just the annotated graph.
# TODO(eriq): How do we fix the size?
Inputs = container.List
Outputs = container.List

# TODO(eriq): Include all edges in targets? (param)
# TODO(eriq): Use the training data for weight learning?

PSL_MODEL = 'link_prediction'

class LinkPredictionHyperparams(meta_hyperparams.Hyperparams):
    psl_options = meta_hyperparams.Hyperparameter(
            default = '',
            semantic_types = ['https://metadata.datadrivendiscovery.org/types/ControlParameter'])

    psl_temp_dir = meta_hyperparams.Hyperparameter(
            default = os.path.join('data', 'psl'),
            semantic_types = ['https://metadata.datadrivendiscovery.org/types/ControlParameter'])

    postgres_db_name = meta_hyperparams.Hyperparameter(
            default = 'psl_d3m',
            semantic_types = ['https://metadata.datadrivendiscovery.org/types/ControlParameter'])

class LinkPredictionParams(meta_params.Params):
    debug_options: typing.Dict

class LinkPrediction(pi_supervised_learning.SupervisedLearnerPrimitiveBase[Inputs, Outputs, LinkPredictionParams, LinkPredictionHyperparams]):
    """
    A primitive that performs link prediction on an annotated graph.
    """

    def __init__(self, *, hyperparams: LinkPredictionHyperparams, random_seed: int = 0, _debug_options: typing.Dict = {}) -> None:
        super().__init__(hyperparams = hyperparams, random_seed = random_seed)

        self._logger = get_logger(__name__)

        self._set_debug_options(_debug_options)

    def _set_debug_options(self, _debug_options):
        self._debug_options = _debug_options

        if (DEBUG_OPTION_LOGGING_LEVEL in _debug_options):
            set_logging_level(_debug_options[DEBUG_OPTION_LOGGING_LEVEL])

    def produce(self, *, inputs: Inputs, timeout: float = None, iterations: int = None) -> pi_base.CallResult[Outputs]:
        self._logger.debug("Starting produce")

        annotatedGraph = self._validateInputs(inputs)
        result = self._link_prediction(annotatedGraph)

        outputs: container.List = container.List([result])
        metaInfo = {
            'schema': meta_base.CONTAINER_SCHEMA_VERSION,
            'structural_type': type(outputs),
            'dimension': {
                'length': len(outputs)
            }
        }
        metadata = inputs.metadata.clear(metaInfo, for_value = outputs, source=self)
        metadata = metadata.update((meta_base.ALL_ELEMENTS,), {'structural_type': int}, source = self)
        outputs.metadata = metadata

        return pi_base.CallResult(outputs)

    def _link_prediction(self, graph):
        write_psl_data(graph, self.hyperparams['psl_temp_dir'])
        pslOutput = run_model(
                PSL_MODEL,
                self.hyperparams['psl_options'],
                self.hyperparams['psl_temp_dir'],
                self.hyperparams['postgres_db_name'])

        return build_output_graph(pslOutput[LINK_PREDICATE], graph)

    def _validateInputs(self, inputs: Inputs):
        if (len(inputs) != 1):
            raise ValueError("Not exactly one input, found %d." % (len(inputs)))

        graph = inputs[0]

        if (not isinstance(graph, Graph)):
            raise ValueError("Expecting a graph, found a %s" % (type(graph).__name__))

        return graph

    def set_training_data(self, *, inputs: Inputs, outputs: Outputs) -> None:
        # Weight learning not yet supported.
        pass

    def fit(self, *, timeout: float = None, iterations: int = None) -> pi_base.CallResult[None]:
        # Weight learning not yet supported.
        return pi_base.CallResult(None)

    def get_params(self) -> LinkPredictionParams:
        return LinkPredictionParams({
            'debug_options': self._debug_options
        })

    def set_params(self, *, params: LinkPredictionParams) -> None:
        self._set_debug_options(params['debug_options'])

    # TODO(eriq): We should implement a can_accept() that ensures we only have a graph-matching problem dataset.

    metadata = meta_base.PrimitiveMetadata({
        # Required
        'id': 'd83aa8fe-0433-4462-be54-b4074959b6fc',
        'version': config.VERSION,
        'name': 'Link Prediction',
        'description': 'Perform collective link prediction.',
        'python_path': 'd3m.primitives.pslgraph.LinkPrediction',
        'primitive_family': meta_base.PrimitiveFamily.LINK_PREDICTION,
        'algorithm_types': [
            meta_base.PrimitiveAlgorithmType.MARKOV_LOGIC_NETWORK,
        ],
        'source': {
            'name': config.D3M_PERFORMER_TEAM,
            'uris': [ config.REPOSITORY ]
        },

        # Optional
        'keywords': [ 'primitive', 'graph', 'link prediction', 'collective classifiction'],
        'installation': [
            config.INSTALLATION,
            config.INSTALLATION_JAVA,
            config.INSTALLATION_POSTGRES
        ],
        'location_uris': [],
        'precondition': [ meta_base.PrimitiveEffects.NO_MISSING_VALUES ],
        'effects': [ meta_base.PrimitiveEffects.NO_MISSING_VALUES ],
        'hyperparms_to_tune': []
    })
