import abc
import json

class BasePipeline(object):
    @abc.abstractmethod
    def gen_pipeline(self):
        pass

    @abc.abstractmethod
    def get_datesets(self):
        '''
        Get the name of datasets compatibile with this pipeline.
        '''
        pass

    @abc.abstractmethod
    def assert_result(self, tester, results, dataset):
        '''
        Make sure that the results from an invocation are valid.
        '''
        pass

    def gen_json(self):
        return json.dumps(json.loads(self.gen_pipeline().to_json()), indent = 4)
