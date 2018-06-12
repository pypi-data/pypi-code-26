import typing

from d3m import container
from d3m.metadata import base as meta_base
from d3m.metadata import hyperparams as meta_hyperparams
from d3m.primitive_interfaces import base as pi_base
from d3m.primitive_interfaces import transformer as pi_transformer
from networkx import Graph as nx_Graph # type: ignore

from . import config
from .constants import *
from .networkx import Graph
from .networkx import DiGraph
from .util import computeNodeLabel
from .util import get_logger
from .util import set_logging_level

Inputs = container.Dataset
Outputs = container.List

class GraphMatchingParserHyperparams(meta_hyperparams.Hyperparams):
    # TODO(eriq): Remove after bug is fixed.
    # There is a bug in the metadata that requires nested hyperparams to have values.
    dummy = meta_hyperparams.Hyperparameter(
            default = 10,
            semantic_types = ['https://metadata.datadrivendiscovery.org/types/ControlParameter'])

class GraphMatchingParser(pi_transformer.TransformerPrimitiveBase[Inputs, Outputs, GraphMatchingParserHyperparams]):
    """
    A primitive that transforms graph matching problems with multiple graphs into a single graph for later processing.
    """

    def __init__(self, *, _debug_options: typing.Dict = {}, hyperparams: GraphMatchingParserHyperparams, random_seed: int = 0) -> None:
        super().__init__(hyperparams = hyperparams, random_seed = random_seed)

        self._logger = get_logger(__name__)

        self._set_debug_options(_debug_options)

    def _set_debug_options(self, _debug_options):
        if (DEBUG_OPTION_LOGGING_LEVEL in _debug_options):
            set_logging_level(_debug_options[DEBUG_OPTION_LOGGING_LEVEL])

    def produce(self, *, inputs: Inputs, timeout: float = None, iterations: int = None) -> pi_base.CallResult[Outputs]:
        self._logger.debug("Starting produce")

        graph1, graph2, observedLinks = self._validate_inputs(inputs)
        result = self._process_data(graph1, graph2, observedLinks)

        outputs: container.List = container.List(result)

        metaInfo = {
            'schema': meta_base.CONTAINER_SCHEMA_VERSION,
            'structural_type': type(outputs),
            'dimension': {
                'length': len(outputs)
            }
        }
        metadata = inputs.metadata.clear(metaInfo, for_value = outputs, source = self)
        metadata = metadata.update((meta_base.ALL_ELEMENTS,), {'structural_type': Graph}, source = self)
        outputs.metadata = metadata

        return pi_base.CallResult(outputs)

    def _validate_inputs(self, inputs: Inputs):
        if (len(inputs) != 3):
            raise ValueError("Dataset does not have three elements. Found %s." % (len(inputs)))

        # TODO(eriq): Fetch these keys from metadata.
        graph1 = inputs['0']
        graph2 = inputs['1']
        observedLinks = inputs['2']

        if (not isinstance(graph1, nx_Graph)):
            raise ValueError("Expecting a graph at \"'0'\", found a %s" % (type(graph1).__name__))

        if (not isinstance(graph2, nx_Graph)):
            raise ValueError("Expecting a graph at \"'1'\", found a %s" % (type(graph2).__name__))

        # Panda's Index, D3M Index, G1 nodeID, G2 nodeID, match

        count = 0
        for row in observedLinks.itertuples():
            # One extra column for the index.
            if (len(row) != 5):
                raise ValueError("Row %d in the tabular data that does not have four columns, found: (%s)." % (count, row))

            # We can't assign back into our Panda's frame, but we can check a failed conversion.
            int(row[2])
            int(row[3])

            if (row[4] != ''):
                val = float(row[4])
                if (val < 0.0 or val > 1.0):
                    raise ValueError("Row %d is out of range, found: (%s)." % (count, val))

            count += 1

        return Graph(graph1), Graph(graph2), observedLinks

    # Return a new graph with properly labeled nodes.
    def _relabel(self, input_graph, node_modifier):
        output_graph = Graph()

        # First add all the nodes.
        for (id, data) in input_graph.nodes(data = True):
            label = computeNodeLabel(data[NODE_ID_LABEL], node_modifier)

            data[SOURCE_GRAPH_KEY] = node_modifier
            data[NODE_ID_LABEL] = data[NODE_ID_LABEL]

            output_graph.add_node(label, **data)

        # Now add all the edges.
        for (source, target, data) in input_graph.edges(data = True):
            source_id = input_graph.node[source][NODE_ID_LABEL]
            target_id = input_graph.node[target][NODE_ID_LABEL]

            # Disallow self edges.
            if (source == target or source_id == target_id):
                continue

            weight = 1.0
            if (WEIGHT_KEY in data):
                weight = data[WEIGHT_KEY]

            # Remember, these edges are within the same input graph.
            source_label = computeNodeLabel(source_id, node_modifier)
            target_label = computeNodeLabel(target_id, node_modifier)

            data[WEIGHT_KEY] = weight
            data[EDGE_TYPE_KEY] = EDGE_TYPE_EDGE
            data[OBSERVED_KEY] = True

            output_graph.add_edge(source_label, target_label, **data)

        return output_graph

    def _process_data(self, graph1, graph2, observedLinks):
        self._logger.debug("Processing data")

        graph1 = self._relabel(graph1, NODE_MODIFIER_SOURCE)
        graph2 = self._relabel(graph2, NODE_MODIFIER_TARGET)

        # Panda's Index, D3M Index, G1 nodeID, G2 nodeID, match

        # Build up the graph of observed links.
        observedGraph = DiGraph()
        for row in observedLinks.itertuples():
            # If there is no weight, then this is test data,
            # Skip this link.
            # TODO(eriq): Think about this more.
            if (row[3] == None):
                continue

            source = int(row[2])
            target = int(row[3])

            weight = None
            if (row[4] != ''):
                weight = float(row[4])

            sourceLabel = computeNodeLabel(source, NODE_MODIFIER_SOURCE)
            targetLabel = computeNodeLabel(target, NODE_MODIFIER_TARGET)

            attributes = {
                SOURCE_GRAPH_KEY: NODE_MODIFIER_SOURCE,
                NODE_ID_LABEL: source,
            }
            observedGraph.add_node(sourceLabel, **attributes)

            attributes = {
                SOURCE_GRAPH_KEY: NODE_MODIFIER_TARGET,
                NODE_ID_LABEL: target,
            }
            observedGraph.add_node(targetLabel, **attributes)

            observedGraph.add_edge(sourceLabel, targetLabel, weight = weight)

        # Add in some hints 
        # We know that it makes sense to compute the local feature based similarity of the links.
        for graph in [graph1, graph2, observedGraph]:
            graph.metadata = graph.metadata.update([], {
                'schema': meta_base.CONTAINER_SCHEMA_VERSION,
                'structural_type': Graph,
                'hints': {
                    GRAPH_HINT_LINK_LOCAL_SIM: True
                }
            })

        return [graph1, graph2, observedGraph]

    # TODO(eriq): We should implement a can_accept() that ensures we only have a graph-matching problem dataset.

    metadata = meta_base.PrimitiveMetadata({
        # Required
        'id': '3c4a1c2a-0f88-4fb1-a1b5-23226a38741b',
        'version': config.VERSION,
        'name': 'Graph Matching Parser',
        'description': 'Transform "graph matching"-like problems into pure graphs.',
        'python_path': 'd3m.primitives.pslgraph.GraphMatchingParser',
        'primitive_family': meta_base.PrimitiveFamily.DATA_TRANSFORMATION,
        'algorithm_types': [
            meta_base.PrimitiveAlgorithmType.COMPUTER_ALGEBRA,
        ],
        'source': {
            'name': config.D3M_PERFORMER_TEAM,
            'uris': [ config.REPOSITORY ]
        },

        # Optional
        'keywords': [ 'preprocessing', 'primitive', 'graph', 'dataset', 'transformer'],
        'installation': [ config.INSTALLATION ],
        'location_uris': [],
        'precondition': [ meta_base.PrimitiveEffects.NO_MISSING_VALUES ],
        'effects': [ meta_base.PrimitiveEffects.NO_MISSING_VALUES ],
        'hyperparms_to_tune': []
    })
