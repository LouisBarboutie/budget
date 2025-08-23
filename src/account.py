from datetime import datetime
import dateutil

import pandas as pd
import numpy as np


class Account:

    def __init__(self, dataframe: pd.DataFrame):
        self.dataframe = dataframe

    def monthly_averages(self, start: datetime, stop: datetime) -> dict:
        filtered_dataframe = self.dataframe.loc[
            (self.dataframe["Date"] >= start) & (self.dataframe["Date"] < stop)
        ]

        # Get the total expenses per month and category
        date_index = pd.PeriodIndex(filtered_dataframe["Date"], freq="M")
        grouped_dataframe = filtered_dataframe.groupby([date_index, "Category"])
        monthly_sums = grouped_dataframe["Operation"].sum()

        # Reshape the dataframe to take the mean more easily
        monthly_sums = monthly_sums.unstack(fill_value=0)
        monthly_averages = monthly_sums.mean(axis=0)

        return monthly_averages.to_dict()

    def get_cumulative_monthly(self, month: str | datetime) -> tuple[np.ndarray]:

        if isinstance(month, str):
            month = dateutil.parser.parse(month)
        start = month.replace(day=1)
        stop = month.replace(month=month.month + 1, day=1)

        filtered_dataframe = self.dataframe.loc[
            (self.dataframe["Date"] >= start)
            & (self.dataframe["Date"] < stop)
            & (self.dataframe["Operation"] < 0)
            & (self.dataframe["Category"] != "Transaction exclue")
        ]
        cumulative_expenses = filtered_dataframe["Operation"].cumsum()
        dates = filtered_dataframe["Date"]

        return cumulative_expenses.to_numpy(), dates.to_numpy()
