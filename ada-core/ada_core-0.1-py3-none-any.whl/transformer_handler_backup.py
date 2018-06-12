# """
# Author: qiacai
# """
#
#
# """
# API for Time Series Transformation Module
# This module transform a time series into time series(s),
# currently only consider single in and single out
# """
#
# from ada_core.data.time_series import TimeSeries
# from ada_core.algorithms.transformer.all import transformers_pool
# from ada_core import exceptions
#
#
# class TransformerHandlerBackup(object):
#
#     def __init__(self, time_series: TimeSeries or dict, transformer_configs: str or tuple or list):
#         """
#         Initializer
#
#         :param time_series: the input time_series
#         :param transformer:
#         :return:
#         """
#
#         self.time_series = TransformerHandler._load(time_series)
#         self.transformer = None
#         self.params = {}
#
#         if not transformer_configs:
#             raise exceptions.ParametersNotPassed('ada_core.TransformerWorker config not correct.')
#
#         elif isinstance(transformer_configs, str) or isinstance(transformer_configs, tuple):
#             self.transformer, self.params = TransformerHandler._parse_config(transformer_configs)
#             self.params = self.params or {}
#             self.params = self.params.update({'time_series': self.time_series})
#             self._work()
#
#         elif isinstance(transformer_configs, list):
#             for i in range(len(transformer_configs)):
#                 transformer_config = transformer_configs[i]
#
#                 if not transformer_config or not isinstance(transformer_config, str) or not isinstance(transformer_config, tuple):
#                     raise exceptions.ParametersNotPassed('ada_core.TransformerWorker config not correct at {}th.'.format(i))
#                 else:
#                     self.transformer, self.params = TransformerHandler._parse_config(transformer_config)
#                     self.params = self.params or {}
#                     self.params = self.params.update({'time_series': self.time_series})
#                     self._work()
#
#         else:
#             raise exceptions.ParametersNotPassed('ada_core.TransformerWorker config not correct.')
#
#     @staticmethod
#     def _load(time_series):
#         """
#         Load Time Series
#
#         :param time_series:
#         :return:
#         """
#
#         if not time_series:
#             return None
#         if isinstance(time_series, TimeSeries):
#             return time_series
#         elif isinstance(time_series, dict):
#             return TimeSeries(time_series)
#         else:
#             return None
#
#     @staticmethod
#     def _get_transformer(transformer_name: str):
#         """
#         Get the specific transformer
#
#         :param transformer_name:
#         :return:
#         """
#
#         try:
#             transformer = transformers_pool[transformer_name]
#             return transformer
#         except KeyError:
#             raise exceptions.AlgorithmNotFound('ada_core.Transformer: ' + str(transformer_name) + 'not found.')
#
#     @staticmethod
#     def _parse_config(transformer_config):
#         if not transformer_config:
#             raise exceptions.ParametersNotPassed('ada_core.TransformerWorker._parse_config config not correct.')
#
#         if isinstance(transformer_config, str):
#             transformer = TransformerHandler._get_transformer(transformer_config)
#             params = {}
#             return transformer, params
#
#         if isinstance(transformer_config, tuple):
#             if len(transformer_config) != 2:
#                 raise exceptions.ParametersNotPassed('ada_core.TransformerWorker._parse_config ' + str(transformer_config) + ' config not correct.')
#
#             transformer_name = transformer_config[0]
#             if not transformer_name or not isinstance(transformer_name, str):
#                 raise exceptions.ParametersNotPassed('ada_core.TransformerWorker._parse_config ' + str(transformer_config) + ' config not correct.')
#             transformer = TransformerHandler._get_transformer(transformer_name)
#             params = transformer_config[1] or {}
#             return transformer, params
#
#     def _work(self):
#         """
#         Run the transformer
#         :return:
#         """
#
#         transformer_obj = self.transformer(**self.params)
#
#         self.time_series = transformer_obj.run()
#
#     def get_ts(self):
#
#         """
#         Get the transformered time series
#         :return:
#         """
#
#         return getattr(self, 'time_series', None)
