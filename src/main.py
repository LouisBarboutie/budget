from datetime import datetime

import pandas as pd
import matplotlib.pyplot as plt

from parsers import parse_banque_populaire_csv
from account import Account
import plot


if __name__ == "__main__":
    df1 = parse_banque_populaire_csv("../data/30042025_248079.csv")
    df2 = parse_banque_populaire_csv("../data/16082025_248079.csv")

    df = pd.concat([df1, df2], ignore_index=True)
    df.sort_values(by="Date", inplace=True)

    account = Account(df)

    plot.operations(account)

    date_start = datetime(year=2025, month=4, day=1)
    date_stop = datetime(year=2025, month=8, day=1)
    plot.display_monthly_averages(account, date_start, date_stop)

    plot.pie_monthly(account, date_start)

    plot.cumulative_monthly(account, datetime(2025, 5, 1))

    plot.cumulative_histogram(account, "March 2025", "Aug 2025", include_end=True)
    plt.show()
