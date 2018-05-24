# pylint: disable=no-self-use,invalid-name,protected-access
import os
import shutil

from allennlp.common.testing import AllenNlpTestCase
from allennlp.training.metrics import WikiTablesAccuracy
from allennlp.training.metrics.wikitables_accuracy import SEMPRE_DIR


class WikiTablesAccuracyTest(AllenNlpTestCase):
    def setUp(self):
        super().setUp()
        self.should_remove_sempre_dir = not os.path.exists(SEMPRE_DIR)

    def tearDown(self):
        super().tearDown()
        if self.should_remove_sempre_dir and os.path.exists(SEMPRE_DIR):
            shutil.rmtree('data')

    def test_accuracy_is_scored_correctly(self):
        # This is the first example in our test fixture.
        example_string = ('(example (id nt-0) (utterance "what was the last year where this team '
                          'was a part of the usl a-league?") (context (graph '
                          'tables.TableKnowledgeGraph tables/590.csv)) '
                          '(targetValue (list (description "2004"))))')

        # This logical form should produce the correct denotation (the "targetValue" above) given
        # the table.
        logical_form = ('((reverse fb:row.row.year) (fb:row.row.index (max '
                        '((reverse fb:row.row.index) (fb:row.row.league fb:cell.usl_a_league)))))')

        wikitables_accuracy = WikiTablesAccuracy(table_directory='tests/fixtures/data/wikitables/')
        wikitables_accuracy(logical_form, example_string)
        assert wikitables_accuracy._count == 1
        assert wikitables_accuracy._correct == 1

        # Testing that we handle bad logical forms correctly.
        wikitables_accuracy(None, example_string)
        assert wikitables_accuracy._count == 2
        assert wikitables_accuracy._correct == 1

        wikitables_accuracy('Error producing logical form', example_string)
        assert wikitables_accuracy._count == 3
        assert wikitables_accuracy._correct == 1

        # And an incorrect logical form.
        wikitables_accuracy('(fb:row.row.league fb:cell.3rd_usl_3rd)', example_string)
        assert wikitables_accuracy._count == 4
        assert wikitables_accuracy._correct == 1
