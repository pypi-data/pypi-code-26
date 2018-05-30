class FeatureProducer:
    def __init__(self, feature_label):
        """
        :param feature_label: The label you like for new feature.
        """
        self.feature_label = feature_label

    def produce(self, df):
        """
        Produce a new feature based on given dataframe.

        :param df: A dataframe that is indexed by pd.DatetimeIndex, and has columns of open, high, low, close, volume as float.
        :return: A new dataframe that has the new feature column added.
        """
        pass


class FeatureProducerPipeline(FeatureProducer):
    """
    This gives users the ability to combine several feature producers into a pipeline.
    One can create a list of solid producer instances and put them in the pipeline to construct
    a big new producer.
    """
    def __init__(self, producers):
        FeatureProducer.__init__(self, None)
        self.producers = producers

    def produce(self, df):
        """
        Iterate the given dataframe through all the producers in the list.
        :param df: A dataframe that is indexed by pd.DatetimeIndex, and has columns of open, high, low, close, volume as float.
        :return: A new dataframe that has all the new feature columns produced by each producer
        """
        result = df.copy()
        for p in self.producers:
            result = p.produce(result)

        return result
