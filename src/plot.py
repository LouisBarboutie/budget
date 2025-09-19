from datetime import datetime, timedelta
import dateutil
from typing import Optional

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdt
from prettytable import PrettyTable

from account import Account
from colors import CATEGORY_COLORS


def display_monthly_averages(account: Account, start: datetime, stop: datetime) -> None:

    averages = account.monthly_averages(start, stop)

    start = start.strftime("%B %Y")
    stop = (stop.replace(day=1) - timedelta(days=1)).strftime("%B %Y")
    title = f"Average expenses for the period {start} to {stop}"

    table = PrettyTable(["Category", "Value"], title=title, float_format=".2")
    table.align["Value"] = "r"

    for category, average in averages.items():
        if category == "Transaction exclue":
            continue
        table.add_row([category, average])
    table.sortby = "Value"
    table.sort_key(lambda x: -x)

    print(table)

    table = PrettyTable(["", "Total"], float_format=".2")
    table.align["Total"] = "r"
    expenses = sum([average for average in averages.values() if average < 0])
    revenue = sum([average for average in averages.values() if average > 0])
    balance = revenue + expenses
    table.add_rows(
        [
            ["Total expenses", expenses],
            ["Total revenue", revenue],
            ["Balance", balance],
        ],
        divider=True,
    )

    print(table)

    return


def expenses(
    account: Account, start: str | datetime, stop: Optional[str | datetime]
) -> plt.Figure:
    """TODO"""

    dates, operations = account.expenses(start, stop)

    fig, ax = plt.subplots()
    ax.plot(dates, np.abs(operations))

    fmt = "%d %B %Y"
    fig.suptitle(
        f"Expenses for the dates of {start.strftime(fmt)} to {stop.strftime(fmt)}"
    )
    ax.set_ylabel("Expenses [€]")
    ax.xaxis.set_major_formatter(mdt.DateFormatter("%b %Y"))
    ax.xaxis.set_major_locator(mdt.MonthLocator())
    ax.tick_params(axis="x", labelrotation=45)

    return fig


def income(
    account: Account, start: str | datetime, stop: Optional[str | datetime]
) -> plt.Figure:
    """TODO"""

    dates, operations = account.revenue(start, stop)

    fig, ax = plt.subplots()
    ax.plot(dates, np.abs(operations))

    fmt = "%d %B %Y"
    fig.suptitle(
        f"Expenses for the dates of {start.strftime(fmt)} to {stop.strftime(fmt)}"
    )
    ax.set_ylabel("Expenses [€]")
    ax.xaxis.set_major_formatter(mdt.DateFormatter("%b %Y"))
    ax.xaxis.set_major_locator(mdt.MonthLocator())
    ax.tick_params(axis="x", labelrotation=45)

    return fig


def pie_monthly(
    account: Account, month: datetime, min_contribution: float = 0.05
) -> plt.Figure:

    start = month
    stop = datetime(month.year, month.month + 1, 1)
    sub_dataframe = account.dataframe.loc[
        (account.dataframe["Date"] >= start) & (account.dataframe["Date"] < stop)
    ]
    sub_dataframe = sub_dataframe.loc[sub_dataframe["Operation"] < 0]
    grouped_sums = sub_dataframe.groupby("Category")["Operation"].sum()
    grouped_sums = grouped_sums.drop("Transaction exclue").sort_values()

    sums = np.abs(grouped_sums.values)
    total = np.sum(sums)

    mask = sums / total > min_contribution
    debit = sums[mask]
    labels = grouped_sums.keys().to_numpy()[mask]
    colors = [CATEGORY_COLORS[category] for category in labels]

    if mask.size > 0:
        debit = np.append(debit, total - np.sum(debit))
        labels = np.append(labels, "Other")
        colors += ["grey"]

    fig, ax = plt.subplots()
    fig.suptitle(f"Expenses for {month.strftime("%B %Y")}")
    ax.text(
        0,
        0,
        f"Total:\n{total:.2f}€",
        horizontalalignment="center",
        verticalalignment="center",
    )
    ax.pie(
        debit,
        autopct="%1.1f%%",
        pctdistance=0.7,
        radius=0.75,
        labels=labels,
        colors=colors,
        wedgeprops={"linewidth": 2, "edgecolor": "white", "width": 0.5},
    )

    return fig


def cumulative_histogram(
    account: Account,
    start: str | datetime,
    stop: Optional[str | datetime] = None,
) -> plt.Figure:

    if isinstance(start, str):
        start = dateutil.parser.parse(start)
    start = start.replace(day=1)

    if stop is None:
        stop = start.replace(month=start.month + 1)
    if isinstance(stop, str):
        stop = dateutil.parser.parse(stop)
    stop = stop.replace(day=1)

    expenses, dates = account.get_cumulative_monthly(start, stop)

    widths = np.zeros_like(dates)
    widths[:-1] = dates[1:] - dates[:-1]
    widths[-1] = np.datetime64(stop) - dates[-1]

    fig, ax = plt.subplots()
    ax.bar(dates, np.abs(expenses), widths, align="edge")

    FORMAT = "%B %Y"
    fig.suptitle(
        f"Cumulative expenses for the period of {start.strftime(FORMAT)} to {stop.strftime(FORMAT)}"
    )
    ax.set_ylabel("Cumulative expenses (€)")
    ax.xaxis.set_major_formatter(mdt.DateFormatter("%b %Y"))
    ax.xaxis.set_major_locator(mdt.MonthLocator())
    ax.xaxis.set_minor_locator(mdt.DayLocator())
    ax.tick_params(axis="x", labelrotation=45)

    return fig
