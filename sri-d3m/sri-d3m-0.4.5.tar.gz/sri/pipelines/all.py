# Information on all pipelines and which primitives are used.

import json

from sri.pipelines.base import BasePipeline
from sri.pipelines.baseline_mean import MeanBaselinePipeline
from sri.pipelines.collaborative_filtering import CollaborativeFilteringParserPipeline
from sri.pipelines.collaborative_filtering_link_prediction import CollaborativeFilteringLinkPredictionPipeline
from sri.pipelines.collaborative_filtering_transform import CollaborativeFilteringTransformPipeline
from sri.pipelines.collaborative_filtering_transform_lp import CollaborativeFilteringTransformLPPipeline
from sri.pipelines.graph_matching import GraphMatchingParserPipeline
from sri.pipelines.graph_matching_link_prediction import GraphMatchingLinkPredictionPipeline
from sri.pipelines.graph_matching_transform import GraphMatchingTransformPipeline
from sri.pipelines.graph_matching_transform_lp import GraphMatchingTransformLPPipeline

from sri.baseline.mean import MeanBaseline
from sri.graph.collaborative_filtering import CollaborativeFilteringParser
from sri.graph.graph_matching import GraphMatchingParser
from sri.graph.transform import GraphTransformer
from sri.psl.collaborative_filtering_link_prediction import CollaborativeFilteringLinkPrediction
from sri.psl.graph_matching_link_prediction import GraphMatchingLinkPrediction
from sri.psl.link_prediction import LinkPrediction

PIPELINES_BY_PRIMITIVE = {
    'd3m.primitives.sri.baseline.MeanBaseline': [
        MeanBaselinePipeline,
    ],
    'd3m.primitives.sri.graph.CollaborativeFilteringParser': [
        CollaborativeFilteringParserPipeline,
        CollaborativeFilteringTransformPipeline,
        CollaborativeFilteringTransformLPPipeline,
    ],
    'd3m.primitives.sri.graph.GraphMatchingParser': [
        GraphMatchingParserPipeline,
        GraphMatchingTransformPipeline,
        GraphMatchingTransformLPPipeline,
    ],
    'd3m.primitives.sri.graph.GraphTransformer': [
        CollaborativeFilteringTransformPipeline,
        CollaborativeFilteringTransformLPPipeline,
        GraphMatchingTransformPipeline,
        GraphMatchingTransformLPPipeline,
    ],
    'd3m.primitives.sri.psl.CollaborativeFilteringLinkPrediction': [
        CollaborativeFilteringLinkPredictionPipeline,
    ],
    'd3m.primitives.sri.psl.GraphMatchingLinkPrediction': [
        GraphMatchingLinkPredictionPipeline,
    ],
    'd3m.primitives.sri.psl.LinkPrediction': [
        CollaborativeFilteringTransformLPPipeline,
        GraphMatchingTransformLPPipeline,
    ],
}

def get_primitives():
    return PIPELINES_BY_PRIMITIVE.keys()

def get_pipelines(primitive = None):
    if (primitive is not None):
        if (primitive not in PIPELINES_BY_PRIMITIVE):
            return []
        return PIPELINES_BY_PRIMITIVE[primitive]

    pipelines = set()
    for primitive_pipelines in PIPELINES_BY_PRIMITIVE.values():
        pipelines = pipelines | set(primitive_pipelines)
    return pipelines

if __name__ == '__main__':
    print(json.dumps(PIPELINES_BY_PRIMITIVE))
