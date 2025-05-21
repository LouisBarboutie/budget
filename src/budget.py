from dataclasses import dataclass
from enum import IntEnum
import datetime as dt

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdt

HISTORY_COMPTE_CHEQUES = "../data/30042025_248079.csv"
HISTORY_LIVRET_A = "../data/30042025_248081.csv"


class Months(IntEnum):
    JANUARY = 1
    FEBRUARY = 2
    MARCH = 3
    APRIL = 4
    MAY = 5
    JUNE = 6
    JULY = 7
    AUGUST = 8
    SEPTEMBER = 9
    OCTOBER = 10
    NOVEMBER = 11
    DECEMBER = 12


@dataclass
class Compte:
    file: str
    dates: np.ndarray = None
    values: np.ndarray = None

    def __post_init__(self) -> None:
        self.get_operations()
        self.generate_dataframe()
        self.monthly_averages()

    def get_operations(self) -> None:
        with open(self.file, "r") as file:
            file.readline()
            dates = []
            values = []
            categories = []
            for line in file:
                row = line.split(";")
                dates.append(row[-3])
                if row[-5] == "":
                    values.append(row[-4])
                elif row[-4] == "":
                    values.append(row[-5])
                categories.append(row[-7])
            self.values = np.array(values, dtype=float)
            self.dates = np.array(
                [dt.datetime.strptime(date, "%d/%m/%Y") for date in dates]
            )
            self.categories = np.array(categories)
            self.available_categories = set(
                [str(category) for category in set(self.categories)]
            )

            self.available_months = set([date.strftime("%B-%Y") for date in self.dates])
            self.available_months = sorted(
                [
                    dt.datetime.strptime(month, "%B-%Y")
                    for month in self.available_months
                ]
            )
        return

    def generate_dataframe(self) -> pd.DataFrame:
        data = np.append(self.dates[:, None], self.values[:, None], axis=1)
        data = np.append(data, self.categories[:, None], axis=1)

        self.df = pd.DataFrame(
            data,
            columns=["DATE", "VALUE", "CATEGORY"],
        )

    def plot_category(self, category: str, show: bool = True) -> None:
        df_filtered = self.df.loc[self.df["CATEGORY"] == category]
        x = df_filtered["DATE"].to_numpy()
        y = df_filtered["VALUE"].to_numpy()

        fig, ax = plt.subplots()
        fig.suptitle(category)
        ax.xaxis.set_major_formatter(mdt.DateFormatter("%b %Y"))
        ax.xaxis.set_major_locator(mdt.MonthLocator())
        ax.tick_params(axis="x", labelrotation=45)
        ax.scatter(x, y)
        ax.grid()

        if show:
            plt.show()

    def plot_cumulative(self, category: str) -> None:
        df_filtered = self.df.loc[self.df["CATEGORY"] == category]
        x = df_filtered["DATE"].to_numpy()
        y = df_filtered["VALUE"].to_numpy()

        years = x.astype("datetime64[Y]").astype(int) + 1970
        months = x.astype("datetime64[M]").astype(int) % 12 + 1

        pairs = [f"{year}-{month:02d}" for year, month in zip(years, months)]
        pairs = np.unique(pairs)

        monthly_expenses = []
        monthly_dates = []
        bar_widths = []
        for i in range(len(pairs) - 1):
            filtered_df = self.df.loc[
                (self.df["DATE"] >= str(pairs[i]))
                & (self.df["DATE"] < str(pairs[i + 1]))
                & (self.df["CATEGORY"] == category)
            ]
            vals = filtered_df["VALUE"].to_numpy()[::-1]
            dates = filtered_df["DATE"].to_numpy()[::-1]

            next_month = int(pairs[i][-2:]) + 1
            next_year = int(pairs[i][:-3])
            if next_month > 12:
                next_month = 1
                next_year = next_year + 1
            next_month = f"{next_year}-{next_month:02d}"
            widths = list(np.diff(dates)) + [np.datetime64(next_month) - dates[-1]]

            monthly_expenses.append(np.cumsum(np.abs(vals)))
            monthly_dates.append(dates)
            bar_widths.append(widths)

        fig, ax = plt.subplots()
        fig.suptitle(f"{category} cumulative expenses")
        ax.xaxis.set_major_formatter(mdt.DateFormatter("%b %Y"))
        ax.xaxis.set_major_locator(mdt.MonthLocator())
        ax.tick_params(axis="x", labelrotation=45)
        for dates, vals, width in zip(monthly_dates, monthly_expenses, bar_widths):
            ax.bar(dates, vals, width=width, align="edge")
        return

    def monthly_averages(self):
        return


if __name__ == "__main__":
    livret_a = Compte(HISTORY_LIVRET_A)
    compte_cheques = Compte(HISTORY_COMPTE_CHEQUES)

    for category in compte_cheques.available_categories:
        compte_cheques.plot_cumulative(category)

    # compte_cheques.plot_category(category, show=False)

    plt.show()
