from d3m.metadata import pipeline as meta_pipeline

from .base_pipeline import BasePipeline
from sri.baseline.mean import MeanBaseline

# All datasets pass, some are commented out for speed.
DATASETS = {
    '1491_one_hundred_plants_margin': 319,
    '1567_poker_hand': 205001,
    '185_baseball': 267,
    '196_autoMpg': 100,
    '22_handgeometry': 38,
    '26_radon_seed': 183,
    '27_wordLevels': 1400,
    '299_libras_move': 100,
    '30_personae': 29,
    '313_spectrometer': 103,
    # '31_urbansound': 339,
    '32_wikiqa': 5852,
    '38_sick': 754,
    '4550_MiceProtein': 215,
    '49_facebook': 1208,
    '534_cps_85_wages': 106,
    '56_sunspots': 29,
    '57_hypothyroid': 754,
    '59_umls': 3409,
    '60_jester': 880720,
    '66_chlorineConcentration': 3840,
    # '6_70_com_amazon': 62462,
    # '6_86_com_DBLP': 107228,
    'DS01876': 1759,
    'LL1_net_nomination_seed': 80,
    'LL1_penn_fudan_pedestrian': 134,
    'uu1_datasmash': 45,
    'uu2_gp_hyperparameter_estimation': 100,
    # 'uu3_world_development_indicators': 2461,
    'uu4_SPECT': 81,
}

class MeanBaselinePipeline(BasePipeline):
    def get_datasets(self):
        return list(DATASETS.keys())

    def gen_pipeline(self):
        pipeline = meta_pipeline.Pipeline(context = meta_pipeline.PipelineContext.TESTING)
        pipeline.add_input(name = 'inputs')

        step_0 = meta_pipeline.PrimitiveStep(primitive_description = MeanBaseline.metadata.query())
        step_0.add_argument(
                name = 'inputs',
                argument_type = meta_pipeline.ArgumentType.CONTAINER,
                data_reference = 'inputs.0'
        )
        step_0.add_output('produce')
        pipeline.add_step(step_0)

        # Adding output step to the pipeline
        pipeline.add_output(name = 'results', data_reference = 'steps.0.produce')

        return pipeline

    def assert_result(self, tester, results, dataset):
        # The results are always nested.
        tester.assertEquals(len(results), 1)
        tester.assertEquals(len(results[0]), DATASETS[dataset])

if __name__ == '__main__':
    # Pretty print
    print(MeanBaselinePipeline().gen_json())
