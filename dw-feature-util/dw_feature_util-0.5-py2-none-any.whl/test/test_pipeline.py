import pandas as pd
from feature_util import FeatureProducerPipeline
from feature_util.ohlc import (SimpleMovingAverageFeatureProducer, PercentChangeFeatureProducer, TimeLagsFeatureProducer)


def test_pipeline():
    ohlc_df = pd.DataFrame([
        {'open': 1, 'high': 9, 'low': 1, 'close': 1, 'volume': 100},
        {'open': 1, 'high': 8, 'low': 1, 'close': 2, 'volume': 100},
        {'open': 1, 'high': 7, 'low': 1, 'close': 3, 'volume': 100},
        {'open': 1, 'high': 6, 'low': 1, 'close': 4, 'volume': 100},
        {'open': 1, 'high': 5, 'low': 1, 'close': 5, 'volume': 100},
        {'open': 1, 'high': 4, 'low': 1, 'close': 6, 'volume': 100},
        {'open': 1, 'high': 3, 'low': 1, 'close': 7, 'volume': 100}
    ])

    close_5_sma_producer = SimpleMovingAverageFeatureProducer()
    open_pct_change_producer = PercentChangeFeatureProducer(feature='open')
    volume_1_tlag_producer = TimeLagsFeatureProducer(feature='volume', lags=1)

    pipeline = FeatureProducerPipeline([close_5_sma_producer, open_pct_change_producer, volume_1_tlag_producer])
    result = pipeline.produce(ohlc_df)

    assert 'close_sma_5' in result
    assert 'open_pct_change' in result
    assert 'volume_tlag_1' in result

