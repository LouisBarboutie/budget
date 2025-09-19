from datetime import datetime
import dateutil
from typing import Optional

import pandas as pd
import numpy as np


class Account:

    def __init__(self):
        self.dataframe = pd.DataFrame()

    def __repr__(self):
        last = self.dataframe["Date"].max().to_pydatetime()
        first = self.dataframe["Date"].min().to_pydatetime()
        fmt = "%d %B %Y"
        desc = f"The account contains operations for the time period of\n{first.strftime(fmt)}\nto\n{last.strftime(fmt)}"
        return desc

    def add_operations(self, dataframe: pd.DataFrame) -> None:
        self.dataframe = pd.concat([self.dataframe, dataframe], ignore_index=True)
        return

    def expenses(
        self, start: str | datetime, stop: Optional[str | datetime]
    ) -> tuple[np.ndarray, np.ndarray]:
        """Returns the expenses in the given range.

        Parameters
        ----------
        start, stop : str | datetime
            The date range, with the start date included and stop date
            excluded. If `str`, must be parseable by the `dateutil` parser.

        Returns
        -------
        dates, expenses : np.ndarray
        """

        if isinstance(start, str):
            start = dateutil.parser.parse(start)
        if isinstance(stop, str):
            stop = dateutil.parser.parse(stop)

        filtered_df = self.dataframe.loc[
            (self.dataframe["Date"] >= start)
            & (self.dataframe["Date"] < stop)
            & (self.dataframe["Operation"] < 0)
            & (self.dataframe["Category"] != "Transaction exclue")
        ]

        dates = filtered_df["Date"].to_numpy()
        expenses = filtered_df["Operation"].to_numpy()

        return dates, expenses

    def revenue(
        self, start: str | datetime, stop: Optional[str | datetime]
    ) -> tuple[np.ndarray, np.ndarray]:
        """Returns the revenue in the given range.

        Parameters
        ----------
        start, stop : str | datetime
            The date range, with the start date included and stop date
            excluded. If `str`, must be parseable by the `dateutil` parser.

        Returns
        -------
        dates, revenue : np.ndarray
        """

        if isinstance(start, str):
            start = dateutil.parser.parse(start)
        if isinstance(stop, str):
            stop = dateutil.parser.parse(stop)

        filtered_df = self.dataframe.loc[
            (self.dataframe["Date"] >= start)
            & (self.dataframe["Date"] < stop)
            & (self.dataframe["Operation"] > 0)
            & (self.dataframe["Category"] != "Transaction exclue")
        ]

        dates = filtered_df["Date"].to_numpy()
        revenue = filtered_df["Operation"].to_numpy()

        return dates, revenue

    def monthly_averages(self, start: str | datetime, stop: str | datetime) -> dict:
        """Calculates the average of operations per category of a given period.

        Parameters
        ----------
        start, stop : str | datetime
            The averaging range, with the start month included and stop month
            excluded. If `str`, must be parseable by the `dateutil` parser.

        Returns
        -------
        dict
            Contains the categories as keys and averages as values
        """

        if isinstance(start, str):
            start = dateutil.parser.parse(start)
        if isinstance(stop, str):
            stop = dateutil.parser.parse(stop)

        start = start.replace(day=1)
        stop = stop.replace(day=1)

        filtered_dataframe = self.dataframe.loc[
            (self.dataframe["Date"] >= start)
            & (self.dataframe["Date"] < stop)
            & (self.dataframe["Category"] != "Transaction exclue")
        ]

        # Get the total expenses per month and category
        date_index = pd.PeriodIndex(filtered_dataframe["Date"], freq="M")
        grouped_dataframe = filtered_dataframe.groupby([date_index, "Category"])
        monthly_sums = grouped_dataframe["Operation"].sum()

        # Reshape the dataframe to take the mean more easily
        monthly_sums = monthly_sums.unstack(fill_value=0)
        monthly_averages = monthly_sums.mean(axis=0)

        return monthly_averages.to_dict()

    def get_cumulative_monthly(
        self, start: str | datetime, stop: Optional[str | datetime] = None
    ) -> tuple[np.ndarray, np.ndarray]:
        """Calculate the cumulative expenses per month in the given range.

        Parameters
        ----------
        start, stop : str | datetime
            The range of months to cover. The stop date is excluded. If datetime
            type, the day counter is ignored.

        Returns
        -------
        cumulative_expenses : np.ndarray
            The cumulative expenses, reset at 0 at each start of a new month.
        dates : np.ndarray
            The dates corresponding to the day each expense was made.
        """

        if isinstance(start, str):
            start = dateutil.parser.parse(start)
        start = start.replace(day=1)

        if stop is None:
            stop = start.replace(month=start.month + 1, day=1)
        if isinstance(stop, str):
            stop = dateutil.parser.parse(stop)
        stop = stop.replace(day=1)

        filtered_dataframe = self.dataframe.loc[
            (self.dataframe["Date"] >= start)
            & (self.dataframe["Date"] < stop)
            & (self.dataframe["Operation"] < 0)
            & (self.dataframe["Category"] != "Transaction exclue")
        ]
        date_index = pd.PeriodIndex(filtered_dataframe["Date"], freq="M")
        grouped_dataframe = filtered_dataframe.groupby(date_index)
        cumulative_expenses = grouped_dataframe["Operation"].cumsum()
        dates = filtered_dataframe["Date"]

        return cumulative_expenses.to_numpy(), dates.to_numpy()
