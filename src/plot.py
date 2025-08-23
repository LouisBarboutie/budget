from datetime import datetime, timedelta
import dateutil

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdt
from prettytable import PrettyTable

from account import Account
from colors import category_colors


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

    return


def operations(account: Account) -> plt.Figure:

    dates = account.dataframe["Date"].to_numpy()
    operations = account.dataframe["Operation"].to_numpy()

    fig, ax = plt.subplots()
    ax.plot(dates, operations)
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
    colors = [category_colors[category] for category in labels]

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
        # explode=explode,
        radius=0.75,
        labels=labels,
        # rotatelabels=True,
        colors=colors,
        wedgeprops={"linewidth": 2, "edgecolor": "white", "width": 0.5},
    )

    return fig


def cumulative_monthly(account: Account, month: datetime) -> plt.Figure:
    expenses, dates = account.get_cumulative_monthly(month)
    fig, ax = plt.subplots()
    ax.scatter(dates, expenses)
    ax.xaxis.set_major_formatter(mdt.DateFormatter("%d %b %Y"))
    ax.xaxis.set_major_locator(mdt.DayLocator())
    ax.tick_params(axis="x", labelrotation=45)

    return fig


def cumulative_histogram(
    account: Account, start_month: str, end_month: str, include_end: bool = False
) -> plt.Figure:

    start_date = dateutil.parser.parse(start_month)
    end_date = dateutil.parser.parse(end_month)

    # reset day to first of month because parser gives random number if no
    # day is included in the input str
    start_date = start_date.replace(day=1)
    end_date = end_date.replace(day=1)

    if include_end:
        next_month = (end_date.month + 1) % 12
        next_year = end_date.year + (end_date.month + 1) // 12
        end_date = end_date.replace(month=next_month, year=next_year)

    filtered_dataframe = account.dataframe.loc[
        (account.dataframe["Date"] >= start_date)
        & (account.dataframe["Date"] < end_date)
        & (account.dataframe["Operation"] < 0)
        & (account.dataframe["Category"] != "Transaction exclue")
    ]

    date_index = pd.PeriodIndex(filtered_dataframe["Date"], freq="M")
    grouped_dataframe = filtered_dataframe.groupby(date_index)
    expenses = grouped_dataframe["Operation"].cumsum().to_numpy()
    dates = filtered_dataframe["Date"].to_numpy()

    fig, ax = plt.subplots()
    ax.plot(dates, expenses)
    ax.xaxis.set_major_formatter(mdt.DateFormatter("%b %Y"))
    ax.xaxis.set_major_locator(mdt.MonthLocator())
    ax.xaxis.set_minor_locator(mdt.DayLocator())
    ax.tick_params(axis="x", labelrotation=45)

    start = start_date.strftime("%B %Y")
    end = end_date.strftime("%B %Y")
    fig.suptitle(f"Cumulative expenses for the period of {start} to {end}")
    ax.set_ylabel("Cumulative expenses (€)")

    fig2, ax = plt.subplots()
    ax.xaxis.set_major_formatter(mdt.DateFormatter("%b %Y"))
    ax.xaxis.set_major_locator(mdt.MonthLocator())
    ax.tick_params(axis="x", labelrotation=45)

    widths = np.zeros_like(dates)
    widths[:-1] = dates[1:] - dates[:-1]
    widths[-1] = np.datetime64(end_date) - dates[-1]

    ax.bar(dates, np.abs(expenses), widths, align="edge")

    return fig
