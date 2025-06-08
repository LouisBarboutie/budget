from dataclasses import dataclass
from enum import IntEnum
import datetime as dt

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdt
import matplotlib.colors as mcolor

HISTORY_COMPTE_CHEQUES = "../data/30042025_248079.csv"
HISTORY_LIVRET_A = "../data/30042025_248081.csv"

category_colors = {
    "Transaction exclue": "grey",
    "Transports": "blue",
    "Logement - maison": "red",
    "Juridique et administratif": "purple",
    "Banque et assurances": "blue",
    "Education et famille": "red",
    "Alimentation": "red",
    "Sante": "orange",
    "Shopping et services": "orange",
    "Revenus et rentrees d'argent": "purple",
    "Loisirs et vacances": "lightblue",
    "A categoriser - rentree d'argent": "grey",
    "A categoriser - sortie d'argent": "grey",
}


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
    """"""

    file: str
    dates: np.ndarray = None
    values: np.ndarray = None
    df: pd.DataFrame = None
    df_monthly: pd.DataFrame = None

    def __post_init__(self) -> None:
        """"""
        self.get_operations()
        self.generate_dataframe()
        self.generate_monthly_dataframe()

    def get_operations(self) -> None:
        """"""
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
            self.available_months = np.array(self.available_months).astype(
                "datetime64[M]"
            )
        return

    def generate_dataframe(self) -> None:
        """"""
        data = np.append(self.dates[:, None], self.values[:, None], axis=1)
        data = np.append(data, self.categories[:, None], axis=1)

        self.df = pd.DataFrame(
            data,
            columns=["DATE", "VALUE", "CATEGORY"],
        )

        return

    def generate_monthly_dataframe(self) -> None:
        """"""

        if self.df is None:
            raise AttributeError(f"No expenses loaded in the account's dataframe")

        dates = self.df["DATE"].to_numpy()
        years = dates.astype("datetime64[Y]").astype(int) + 1970
        months = dates.astype("datetime64[M]").astype(int) % 12 + 1

        next_month = self.find_next_month(dates[0])

        pairs = np.unique([f"{year}-{month:02d}" for year, month in zip(years, months)])

        # The next month is needed for proper filtering
        monthly_dates = np.append(pairs, str(next_month))

        print(f"{months[0]=}", f"{next_month=}", f"{monthly_dates=}", sep="\n")

        self.df_monthly = pd.DataFrame(columns=["DATE", "DEBIT", "CREDIT", "CATEGORY"])

        for i, (current_month, next_month) in enumerate(
            zip(monthly_dates[:-1], monthly_dates[1:])
        ):
            for category in self.available_categories:
                if category == "Transaction exclue":
                    continue
                # filter the operations for the current month and category
                operations = self.df.loc[
                    (self.df["DATE"] >= str(current_month))
                    & (self.df["DATE"] < str(next_month))
                    & (self.df["CATEGORY"] == category),
                    "VALUE",
                ].to_numpy()

                # filter out the operations
                credit = np.sum(operations[operations > 0])
                debit = np.sum(operations[operations < 0])
                row = len(self.df_monthly)

                # update values in the datagrame
                self.df_monthly.loc[row, "DATE"] = current_month
                self.df_monthly.loc[row, "DEBIT"] = debit
                self.df_monthly.loc[row, "CREDIT"] = credit
                self.df_monthly.loc[row, "CATEGORY"] = category

        return

    def plot_category(self, category: str, show: bool = True) -> None:
        """"""
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

    def plot_cumulative_histogram(self, category: str) -> None:
        """"""
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

            monthly_expenses.append(np.abs(np.cumsum(vals)))
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

    def plot_cumulative_monthly(self, category: str) -> None:
        """"""
        monthly_income = []
        monthly_expenses = []
        monthly_net = []
        monthly_dates = []
        widths = []

        dates = self.df_monthly["DATE"].unique().astype("datetime64[M]")

        next_month = self.find_next_month(dates[-1])
        months = np.append(dates, next_month)

        for i, month in enumerate(months[:-1]):
            filtered_df = self.df_monthly.loc[
                (self.df_monthly["DATE"] == str(month))
                & (self.df_monthly["CATEGORY"] == category)
            ]

            credit = filtered_df["CREDIT"].item()
            debit = filtered_df["DEBIT"].item()
            net = -(credit + debit)
            width = (
                (
                    months[i + 1].astype("datetime64[D]")
                    - month.astype("datetime64[D]")
                ).astype(int)
                / 2
                * 0.75
            )
            width = (width * 24).astype("timedelta64[h]")

            monthly_income.append(credit)
            monthly_expenses.append(debit)
            monthly_net.append(net)
            monthly_dates.append(month)
            widths.append(width)

        widths = np.array(widths)

        fig, ax = plt.subplots()
        fig.suptitle(f"{category} cumulative expenses")
        ax.xaxis.set_major_formatter(mdt.DateFormatter("%b %Y"))
        ax.xaxis.set_major_locator(mdt.MonthLocator())
        ax.tick_params(axis="x", labelrotation=45)
        ax.bar(
            np.array(monthly_dates),
            np.abs(monthly_expenses),
            width=-widths,
            color="red",
            align="edge",
            label="Expenses",
        )
        ax.bar(
            monthly_dates,
            monthly_income,
            width=widths,
            color="green",
            align="edge",
            label="Income",
        )
        ax.plot(monthly_dates, monthly_net, label="Net Expenses")
        ax.legend()

        return

    def plot_pie(self, month: str, min_contribution: float = 0.05) -> None:
        """"""
        if not isinstance(month, str):
            month = str(month)

        available_months = self.df_monthly["DATE"].unique().astype(str)
        print(available_months)
        df_filtered = self.df_monthly.loc[self.df_monthly["DATE"] == month]
        print(df_filtered)
        debit = df_filtered["DEBIT"].to_numpy()
        credit = df_filtered["CREDIT"].to_numpy()
        categories = df_filtered["CATEGORY"].to_numpy()

        indices = np.argsort(debit)
        other = np.sum(
            np.abs(
                [
                    val
                    for val in debit[indices]
                    if val != 0 and val >= np.sum(debit) * min_contribution
                ]
            )
        )
        debit = [
            np.abs(val)
            for val in debit[indices]
            if val != 0 and val <= np.sum(debit) * min_contribution
        ]
        colors = [
            category_colors[category]
            for category, val in zip(categories[indices], debit)
            if val != 0 and val >= np.sum(debit) * min_contribution
        ]
        labels = [
            f"{category}:\n{val:.2f}€"
            for category, val in zip(categories[indices], debit)
            if val != 0 and val >= np.sum(debit) * min_contribution
        ]
        debit += [other]
        colors += ["grey"]
        labels += ["Other"]

        explode = [0.05] * len(debit)

        print(categories)
        print(len(debit), len(labels))

        fig, ax = plt.subplots()
        fig.suptitle(f"Expenses for {month}")
        ax.text(
            0,
            0,
            f"Total:\n{np.sum(debit):.2f}€",
            horizontalalignment="center",
            verticalalignment="center",
        )
        ax.pie(
            debit,
            autopct="%1.1f%%",
            pctdistance=0.7,
            # explode=explode,
            radius=0.75,
            labels=labels,
            rotatelabels=True,
            colors=colors,
            wedgeprops={"linewidth": 2, "edgecolor": "white", "width": 0.5},
        )
        return

    def average(
        self,
        category: str,
        start: str | np.datetime64 | None = None,
        end: str | np.datetime64 | None = None,
        include_end: bool = False,
    ) -> None:
        """"""
        if start is None:
            start = self.df_monthly["DATE"].min()
        if end is None:
            end = self.df_monthly["DATE"].max()
            end = self.find_next_month(end)

        vals = self.df_monthly.loc[
            (self.df_monthly["DATE"] >= str(start))
            & (self.df_monthly["DATE"] < str(end))
            & (self.df_monthly["CATEGORY"] == category),
            ["CREDIT", "DEBIT"],
        ].to_numpy()
        avg = np.mean(np.sum(vals, axis=1))

        return avg

    @staticmethod
    def find_next_month(date: np.datetime64) -> "np.datetime64[M]":
        year = date.astype("datetime64[Y]").astype(int) + 1970
        month = date.astype("datetime64[M]").astype(int) % 12 + 1
        if month % 12 != 0:
            next_month = month + 1
            next_year = year
        else:
            next_month = 1
            next_year = year + 1

        next_date = np.datetime64(f"{next_year}-{next_month:02d}").astype(
            "datetime64[M]"
        )

        return next_date


if __name__ == "__main__":
    livret_a = Compte(HISTORY_LIVRET_A)
    compte_cheques = Compte(HISTORY_COMPTE_CHEQUES)

    print(f"Available categories: {compte_cheques.available_categories}")
    # avg = []
    # for category in compte_cheques.available_categories:
    #     avg.append(compte_cheques.average(category, include_end=True))

    #     # compte_cheques.plot_category(category, show=False)
    #     # compte_cheques.plot_cumulative_monthly(category)
    #     # compte_cheques.plot_cumulative_histogram(category)
    # for category, a in zip(compte_cheques.available_categories, avg):
    #     print(f"{category:<32}: {a:>+10.2f}€")
    # avg = np.array(avg)
    # neg = avg[avg < 0]
    # print(f"total budget: {sum(neg)}€")
    for month in compte_cheques.available_months[-1:-2:-1]:
        compte_cheques.plot_pie(month, 0.015)
    plt.show()
