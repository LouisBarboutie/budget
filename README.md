# Personal budget analyser

This small project is intended to get a better overview of my personal budget, 
especially to visualize more details which are not provided by my banking apps 
and to include accounts from various banks. The planned functionalities include spending statistics, plots, budget calculations etc. 

# Usage

```
    python src -f path/to/data2.csv -f path/to/data1.csv month -p "pie" -m "Jan 2025"
```


```
    python src -f path/to/data.csv range -p "all" -start "Jan 2025" -stop "Jul 2025"
```

# Project structure

```
    src/
        __main__.py  # Entry point with cli
        account.py   # Definition of the account class and related mathematical operations
        colors.py    # Color definitions for the plots
        parsers.py   # Readers of the csv files
        plot.py      # Plotting and display utility
```