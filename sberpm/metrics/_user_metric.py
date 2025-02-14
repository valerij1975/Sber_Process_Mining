# Pandas Python module is used in this file.
#   Licence: BSD-3-Clause License
#   Link: https://github.com/pandas-dev/pandas

import pandas as pd

from ._base_metric import BaseMetric


class UserMetric(BaseMetric):
    """
    Class for calculating metrics for users.

    Parameters
    ----------
    data_holder: DataHolder
        Object that contains the event log and the names of its necessary columns.

    time_unit: {'s'/'second', 'm'/'minute', 'h'/'hour', 'd'/'day', 'w'/'week'}, default='day'
        Calculate time/duration values in given format.

    round: int, default=None
        Round float values of the metrics to the given number of decimals.


    Attributes
    ----------
    metrics: pd.DataFrame
        DataFrame that contains all calculated metrics.
    """

    def __init__(self, data_holder, time_unit='hour', round=None):
        super().__init__(data_holder, time_unit, round)
        self._group_column = data_holder.user_column
        self._group_data = self._dh.data.groupby(self._group_column)

    def apply(self):
        """
        Calculate all possible metrics for this object.

        Returns
        -------
        result: pandas.DataFrame
        """
        self.metrics = pd.DataFrame(index=self._dh.data[self._group_column].unique()) \
            .join(self.count()) \
            .join(self.unique_activities()) \
            .join(self.unique_activities_num()) \
            .join(self.unique_ids()) \
            .join(self.unique_ids_num()) \
            .join(self.throughput()) \
            .join(self.workload()) \
            .join(self.calculate_time_metrics(True))

        return self.metrics.sort_values('count', ascending=False)

    def count(self):
        """
        Return total count of users' occurrences in the event log
        (= number of activities they worked on).

        Returns
        -------
        result: pandas.Series
        """
        return self._group_data[self._group_column].count().rename('count')

    def unique_activities(self):
        """
        Return unique activities each user worked on.

        Returns
        -------
        result: pandas.Series
        """
        return self._group_data.agg({self._dh.activity_column: set})[self._dh.activity_column] \
            .rename('unique_activities')

    def unique_activities_num(self):
        """
        Return number of unique activities each user worked on.

        Returns
        -------
        result: pandas.Series
        """
        return self._group_data[self._dh.activity_column].nunique().rename('unique_activities_num')

    def unique_ids(self):
        """
        Return unique IDs each user worked on.

        Returns
        -------
        result: pandas.Series
        """
        return self._group_data.agg({self._dh.id_column: set})[self._dh.id_column].rename('unique_ids')

    def unique_ids_num(self):
        """
        Return number of unique IDs each user worked on.

        Returns
        -------
        result: pandas.Series
        """
        return self._group_data[self._dh.id_column].nunique().rename('unique_ids_num')

    def throughput(self):
        """
        Return the average number of times each user performs an activity per time unit.

        Returns
        -------
        result: pandas.Series
        """
        return (self.count() / self.total_duration()).rename('throughput')

    def workload(self):
        """
        Return the fraction of all actions each user took.

        Returns
        -------
        result: pandas.Series
        """
        return (self.count() / self.count().sum()).rename('workload')
