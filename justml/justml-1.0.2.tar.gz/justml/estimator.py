from __future__ import division
from collections import OrderedDict
import time
import json
import tempfile
import os
import warnings
import logging
import justml
from .utils import convert_X_y_to_csv, convert_X_to_csv, rename_col_y, chunk_csv


logger = logging.getLogger('justml')

def order_dict(d, keys):
    tuples = []
    for key in keys:
        if key in d:
            tuples.append((key, d[key]))
    return OrderedDict(tuples)

class _Estimator(object):

    folder = None
    _resource_fields = [
        'id', 'name', 'pipeline', 'status', 'date_created', 'date_updated',
        'invoke', 'automl_info', 'message'
    ]

    def __init__(self, id=None, name=None, description='', max_fit_time=None, client=None):
        if ((id is None and name is None)
            or (id is not None and name is not None)):
            raise Exception('You must provide either id or name')

        if client is None:
            client = justml.Client()
        self.client = client
        self.description = description
        self.resource = None

        # Get by id
        if id is not None:
            self.resource = self.client.read(self.folder, id)

        # Get by name
        if self.resource is None and name is not None:
            l = self.client.list(self.folder)
            self.resource = next((x for x in l if x['name'] == name), None)

        # Create new estimator
        if self.resource is None:
            if max_fit_time is None:
                parameters = {}
            else:
                parameters = {'max_fit_time': max_fit_time}
            self.resource = self.client.create(self.folder,
                                               name=name,
                                               description=description,
                                               parameters=parameters)

    def delete(self):
        self.client.delete(self.folder, self.id)

    def _refresh(self):
        self.resource = self.client.read(self.folder, self.id)

    def __getattr__(self, name):
        if name in self._resource_fields:
            return self.resource.get(name)
        else:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        if name in self._resource_fields:
            self.resource[name] = value
            id_ = self.resource.get('id')
            if id_:
                self.client.update(self.folder, id_, **self.resource)
        else:
            super(_Estimator, self).__setattr__(name, value)

    def fit(self, X=None, y=None, csvpath=None, col_y='y', wait=True):
        if (X is None or y is None) and csvpath is None:
            raise Exception('You must provide either X and y or csvpath')

        self._refresh()
        prev_date_updated = self.date_updated

        if self.status == 'trained':
            msg ='Estimator is already trained. New fit will erase previous data.'
            logger.warning(msg)
            warnings.warn(msg)

        logger.info("Sending data to train estimator %s..." % self.name)

        # Send data to API
        if X is not None:
            f, csvpath = tempfile.mkstemp(prefix="justml-tmp")
            try:
                convert_X_y_to_csv(X, y, csvpath)
                self.client.fit(self.folder, self.id, csvpath)
            finally:
                os.close(f)
                os.remove(csvpath)
        else:
            if col_y != 'y':
                f, csvpath_ = tempfile.mkstemp(prefix="justml-tmp")
                try:
                    rename_col_y(col_y, csvpath, csvpath_)
                    self.client.fit(self.folder, self.id, csvpath_)
                finally:
                    os.close(f)
                    os.remove(csvpath_)
            else:
                self.client.fit(self.folder, self.id, csvpath)

        # Wait until training is over
        if wait:
            logger.info("Waiting for training to complete on JustML servers...")
            ready = False
            start_time = time.time()
            cur_time = start_time
            max_time = start_time + 24 * 60 * 60
            sleep_time = 15
            while True:
                self._refresh()
                cur_time = time.time()
                date_updated = self.date_updated
                ready = (date_updated != prev_date_updated and self.status != 'training')
                if ready or cur_time >= max_time:
                    break
                time.sleep(sleep_time)

            if cur_time >= max_time and self.status != 'trained':
                raise Exception('Training takes too long, not waiting anymore...')
            if self.status == 'error':
                raise Exception('Error during training. %s' % self.message)
            logger.info("Training is finished, and data has been deleted.")
            logger.debug('Trained in %d seconds' % int(cur_time - start_time))


    def predict(self, X=None, csvpath=None, col_y='y'):
        if X is None and csvpath is None:
            raise Exception('You must provide either X or csvpath')

        self._refresh()
        if not self.pipeline:
            if self.status == 'training':
                raise Exception('Training is in progress. There is no model data yet. '
                                'Try again in a few seconds. '
                                'You can use fit() with wait=True option next time.')
            else:
                raise Exception('There is no model data. Did you run fit()?')
        if self.pipeline and self.status == 'training':
            logger.warning('Training is in progress but there is previous model data available. '
                           'Using previous model data.')
        if X is not None:
            f, csvpath = tempfile.mkstemp(prefix="justml-tmp")
            try:
                convert_X_to_csv(X, csvpath)
                res = self._predict(csvpath)
            finally:
                os.close(f)
                os.remove(csvpath)
        else:
            if col_y != 'y':
                f, csvpath_ = tempfile.mkstemp(prefix="justml-tmp")
                try:
                    rename_col_y(col_y, csvpath, csvpath_)
                    res = self._predict(csvpath_)
                finally:
                    os.close(f)
                    os.remove(csvpath_)
            else:
                res = self._predict(csvpath)
        return res

    def _predict(self, csvpath):
        res = []
        f, tmppath = tempfile.mkstemp(prefix="justml-tmp")
        os.close(f)
        try:
            for _ in chunk_csv(csvpath, tmppath, max_rows=50000):
                res += self.client.predict(self.folder, self.id, tmppath)
        finally:
            os.remove(tmppath)
        return res

    def show_pipeline(self):
        if self.pipeline is not None:
            keys = ["data_preprocessor", "feature_preprocessor", "classifier", "regressor"]
            subkeys = ["step", "class", "args"]
            ordered_pipeline = order_dict(self.pipeline, keys)
            for k, v in ordered_pipeline.items():
                if isinstance(v, (list,)):
                    for i, d in enumerate(v):
                        v[i] = order_dict(d, subkeys)
                else:
                    ordered_pipeline[k] = order_dict(v, subkeys)
            print(json.dumps(ordered_pipeline, indent=4))

    def show_automl_info(self):
        print(json.dumps(self.automl_info, indent=4))


class Classifier(_Estimator):
    folder = '/classifiers/'

class Regressor(_Estimator):
    folder = '/regressors/'
