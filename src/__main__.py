import argparse
import dateutil

import matplotlib.pyplot as plt

from parsers import parse_banque_populaire_csv
from account import Account
import plot

# ------------------------------------------------------------------------------
# Command line interface setup
# ------------------------------------------------------------------------------

RANGE_FUNCTIONS = {
    "cum": plot.cumulative_histogram,
    "exp": plot.expenses,
    "inc": plot.income,
    "avg": plot.display_monthly_averages,
}

MONTH_FUNCTIONS = {
    "pie": plot.pie_monthly,
}

parser = argparse.ArgumentParser()
parser.add_argument(
    "-file", "-f", action="append", required=True, help="File to read the data from"
)
subparsers = parser.add_subparsers()

range_parser = subparsers.add_parser("range")
range_parser.add_argument(
    "-plot", "-p", choices=RANGE_FUNCTIONS.keys(), help="Select plot type to display"
)
range_parser.add_argument("-start", required=True)
range_parser.add_argument("-stop", required=True)

month_parser = subparsers.add_parser("month")
month_parser.add_argument(
    "-plot", "-p", choices=MONTH_FUNCTIONS.keys(), help="Select plot type to display"
)
month_parser.add_argument("-month", "-m", required=True)

args = parser.parse_args()

# ------------------------------------------------------------------------------
# Script execution
# ------------------------------------------------------------------------------

account = Account()
for file in args.file:
    df = parse_banque_populaire_csv(file)
    df.sort_values(by="Date", inplace=True)
    account.add_operations(df)

print(account)

if "month" in args:
    month = dateutil.parser.parse(args.month).replace(day=1)
    MONTH_FUNCTIONS[args.plot](account, month)
else:
    start = dateutil.parser.parse(args.start).replace(day=1)
    stop = dateutil.parser.parse(args.stop).replace(day=1)
    RANGE_FUNCTIONS[args.plot](account, start, stop)

plt.show()
