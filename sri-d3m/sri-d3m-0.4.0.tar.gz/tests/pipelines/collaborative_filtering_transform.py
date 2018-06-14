from d3m.metadata import pipeline as meta_pipeline

from .base_pipeline import BasePipeline
from sri.graph.collaborative_filtering import CollaborativeFilteringParser
from sri.graph.transform import GraphTransformer

class CollaborativeFilteringTransformPipeline(BasePipeline):
    def get_datasets(self):
        return [
            '60_jester'
        ]

    def gen_pipeline(self):
        pipeline = meta_pipeline.Pipeline(context = meta_pipeline.PipelineContext.TESTING)
        pipeline.add_input(name = 'inputs')

        step_0 = meta_pipeline.PrimitiveStep(primitive_description = CollaborativeFilteringParser.metadata.query())
        step_0.add_argument(
                name = 'inputs',
                argument_type = meta_pipeline.ArgumentType.CONTAINER,
                data_reference = 'inputs.0'
        )
        step_0.add_output('produce')
        pipeline.add_step(step_0)

        step_1 = meta_pipeline.PrimitiveStep(primitive_description = GraphTransformer.metadata.query())
        step_1.add_argument(
                name = 'inputs',
                argument_type = meta_pipeline.ArgumentType.CONTAINER,
                data_reference = 'steps.0.produce'
        )
        step_1.add_output('produce')
        pipeline.add_step(step_1)

        # Adding output step to the pipeline
        pipeline.add_output(name = 'Graphs', data_reference = 'steps.1.produce')

        return pipeline

    def assert_result(self, tester, results, dataset):
        tester.assertEquals(len(results), 1)
        tester.assertEquals(len(results[0]), 1)

if __name__ == '__main__':
    # Pretty print
    print(CollaborativeFilteringTransformPipeline().gen_json())
