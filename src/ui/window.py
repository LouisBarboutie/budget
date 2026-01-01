import platform
import datetime
import dateutil

import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from .dateentry import DateEntry
from src.account import Account
from src.plot import pie_monthly
from src.parsers import parse_banque_populaire_csv

if "Windows" in platform.platform():
    from ctypes import windll

    windll.shcore.SetProcessDpiAwareness(1)


class Window:
    def __init__(self):
        self.root = tk.Tk()
        self.root.geometry("1200x900")

        self.file = None

        self.settings_area = tk.Frame(master=self.root)
        self.display_area = tk.Frame(master=self.root)

        self.settings_area.pack(padx=50, side=tk.LEFT, expand=True, anchor=tk.CENTER)
        self.display_area.pack(padx=50, side=tk.LEFT, expand=True, anchor=tk.CENTER)

        # self.figure = Figure()
        # self.axes = self.figure.subplots()
        self.canvas = FigureCanvasTkAgg(master=self.display_area)

        self.graph_selector = ttk.Combobox(master=self.settings_area, values=["pie"])
        self.graph_selector.set("Select a graph type")

        self.file_selector = tk.Button(
            master=self.settings_area, text="Select file", command=self.select_file
        )
        self.plot_button = tk.Button(
            master=self.settings_area, text="Plot!", command=self.plot
        )

        self.start_date_entry = DateEntry(master=self.settings_area)
        self.stop_date_entry = DateEntry(master=self.settings_area)

        self.canvas.get_tk_widget().pack()
        self.file_selector.pack()
        self.graph_selector.pack()
        self.start_date_entry.pack()
        self.stop_date_entry.pack()
        self.plot_button.pack()

    def show(self):
        self.root.mainloop()

    def select_file(self):
        self.file = filedialog.askopenfile(
            title="Select file", filetypes=[("Comma-separated values", "*.csv")]
        )
        print(self.file)

    def plot(self):
        account = Account()
        df = parse_banque_populaire_csv(self.file.name)
        df.sort_values(by="Date", inplace=True)
        account.add_operations(df)

        start = self.start_date_entry.get()
        # stop = self.stop_date_entry.get()
        start_date = dateutil.parser.parse(start, dayfirst=True)
        # stop_date = dateutil.parser.parse(stop)
        figure = pie_monthly(account, start_date)
        width, height = self.canvas.get_width_height(physical=True)
        figure.set_figwidth(width / 100)
        figure.set_figheight(height / 100)
        self.canvas.figure = figure
        self.canvas.draw()


if __name__ == "__main__":
    window = Window()
    window.show()
