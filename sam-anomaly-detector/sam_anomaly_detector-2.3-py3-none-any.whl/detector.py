import os
from datetime import datetime, date
import matplotlib.pyplot as plt

import numpy as np
import pandas as pd
from fbprophet import Prophet


class Detector:
    def __init__(
            self,
            min_time_points: int = 10,
            none_zero_ratio: float = 0.0,
            min_dataset_size: int = 0,
            image_path: str = 'image.png'
    ) -> None:
        self.ds_min_points = min_time_points
        self.none_zero_ratio = none_zero_ratio
        self.min_dataset_size = min_dataset_size
        self.image_path = image_path

        self.x_column_name = 'ds'
        self.y_column_name = 'y'

    def forecast_today(self, dataset: pd.DataFrame) -> pd.DataFrame:
        """
        Forecast today based on history dataset and mark today as anomaly if it's outside of forecasted range
        Input should an array of json objects having `time` & `value` fields
        Output is an array of json objects having today's forecast & anomaly
        :param dataset:
               pd.DataFrame([{"time": "2018-02-13", "value": 1069}, {"time": "2018-02-14", "value": 3000}, ...])
               data should be aggregated per day for example there should be only one entry (value) for each day
        :return: pd.DataFrame of anomalies
                 each Series has "ds", "trend", "trend_lower", "trend_upper", "yhat_lower", "yhat_upper", "seasonal",
                 "seasonal_lower", "seasonal_upper", "seasonalities", "seasonalities_lower", "seasonalities_upper",
                 "weekly", "weekly_lower", "weekly_upper", "yhat", "std", "actual"
                 For more info check https://facebook.github.io/prophet/
        """

        dataset = self._validate_input(dataset)
        historical_data = dataset[:-1]
        last_day_of_data = dataset[-1:]

        todays_forecast = self._get_forecast(historical_data, last_day_of_data)
        return self._compare(historical_data, last_day_of_data, todays_forecast)

    def _validate_input(self, dataset: pd.DataFrame) -> pd.DataFrame:
        x_column_name = 'time'
        y_column_name = 'value'
        if x_column_name not in dataset.columns or y_column_name not in dataset.columns:
            raise ValueError('dataset should have [{}] & [{}] columns'.format(x_column_name, y_column_name))

        dataset = dataset.rename(columns={x_column_name: self.x_column_name, y_column_name: self.y_column_name})

        dataset[self.x_column_name].apply(lambda t: t.strftime('%Y-%m-%d') if isinstance(t, date) else t)

        return dataset

    def _get_forecast(self, data: pd.DataFrame, actual: pd.DataFrame) -> pd.DataFrame:
        actual_time_points = len(data)
        actual_dataset_size = data[self.y_column_name].sum()
        if actual_time_points < self.ds_min_points or (
                len(data[data[self.y_column_name] == 0]) / len(data) > self.none_zero_ratio
        ) or actual_dataset_size < self.min_dataset_size:
            return pd.DataFrame()

        historical_data_last_day = datetime.strptime(data[-1:][self.x_column_name].values[0], '%Y-%m-%d')
        forecast_day = datetime.strptime(actual[self.x_column_name].values[0], '%Y-%m-%d')
        return self._forecast(
            data,
            actual,
            (forecast_day - historical_data_last_day).days
        )

    def _forecast(self, data: pd.DataFrame, actual: pd.DataFrame, days_to_forecast: int) -> pd.DataFrame:
        model = Prophet(daily_seasonality=False, interval_width=0.8)
        prophet_input = pd.DataFrame()
        prophet_input['ds'] = data[self.x_column_name]
        prophet_input['y'] = data[self.y_column_name]
        with suppress_stdout_stderr():
            model.fit(prophet_input)
        future = model.make_future_dataframe(periods=days_to_forecast)
        forecast = model.predict(future)

        if self._is_anomaly(actual, forecast[-1:]):
            fig = plt.figure(facecolor='w', figsize=(10, 6))
            ax = fig.add_subplot(111)
            fig = model.plot(forecast, ax)
            ax.plot(
                [datetime.strptime(d, '%Y-%m-%d') for d in actual[self.x_column_name]],
                actual[self.y_column_name],
                'rx'
            )
            ax.plot(
                [datetime.strptime(d, '%Y-%m-%d') for d in data[self.x_column_name]],
                data[self.y_column_name],
                'k-'
            )
            ax.legend(['history', 'prediction', actual[self.x_column_name].values[0]])
            fig.savefig(self.image_path)
        return forecast[-1:]

    def _compare(self, historical_data: pd.DataFrame, actual: pd.DataFrame, forecast: pd.DataFrame) -> pd.DataFrame:
        anomaly = pd.DataFrame()
        if actual.empty or forecast.empty:
            return pd.DataFrame()

        if self._is_anomaly(actual, forecast):
            anomaly = forecast
            anomaly['prediction'] = forecast['yhat'].values[0]
            history_mean = historical_data[self.y_column_name].mean()
            actual_value = actual[self.y_column_name].values[0]
            anomaly['change'] = (actual_value - history_mean) / history_mean
            anomaly['std_change'] = (actual_value - history_mean) / np.std(historical_data[self.y_column_name])
            anomaly['actual'] = actual_value
            anomaly['image_path'] = self.image_path

        return anomaly

    def _is_anomaly(self, actual, forecast):
        actual_value = actual[self.y_column_name].values[0]
        return actual_value > forecast['yhat_upper'].values[0] or \
               actual_value < forecast['yhat_lower'].values[0]


class suppress_stdout_stderr(object):
    """
    A context manager for doing a "deep suppression" of stdout and stderr
    """

    def __init__(self):
        # Open a pair of null files
        self.null_fds = [os.open(os.devnull, os.O_RDWR) for x in range(2)]
        # Save the actual stdout (1) and stderr (2) file descriptors.
        self.save_fds = (os.dup(1), os.dup(2))

    def __enter__(self):
        # Assign the null pointers to stdout and stderr.
        os.dup2(self.null_fds[0], 1)
        os.dup2(self.null_fds[1], 2)

    def __exit__(self, *_):
        # Re-assign the real stdout/stderr back to (1) and (2)
        os.dup2(self.save_fds[0], 1)
        os.dup2(self.save_fds[1], 2)
        # Close the null files
        os.close(self.null_fds[0])
        os.close(self.null_fds[1])
