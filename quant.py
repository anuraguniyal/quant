import sys
import csv
import datetime

class Day:
    """
    Day represents a day of stock with open/close prices
    """
    def __init__(self, date, open, close, high, low):
        self.date = date
        self.open = open
        self.close = close
        self.high = high
        self.low = low

    @classmethod
    def from_row(cls, row):
        date = datetime.datetime.strptime(row[0], "%Y-%m-%d").date()
        return Day(date, row[1], row[4], row[2], row[3])

class Put:
    def __init__(self, expiry, strike, premium):
        self.expiry = expiry
        self.strike = strike
        self.premium = premium

class Strategy:
    """
    base class for strategy
    """
    def add_day(self, day):
        pass

def calculate_premium(strike_down, expiry_days):
    """
    calculate based on how low the strike is below current price
    and how any days for expiry
    return percent of price
    """
    return strike_down*(expiry_days/5)/10

class BuyPutStrategy(Strategy):
    """
    buy put and wait for collapse
    """
    def __init__(self, strike_down, expiry_days):
        """
        strike_down: precent below current price at which we buy put
        expiry_days: in how many days put expires
        """
        self.strike_down = strike_down
        self.expiry_days = expiry_days
        self.premium = calculate_premium(strike_down, expiry_days)
        self.puts = []

    def add_day(self, day):
        # buy put
        # we assume we buy put at open
        pass

def simulate(csv_path, strategy):
    with open(csv_path) as csv_file:
        reader = csv.reader(csv_file)
        for i, row in enumerate(reader):
            if i == 0:
                continue # skip header
            strategy.add_day(Day.from_row(row))


strategy = BuyPutStrategy(5, 15)

simulate(sys.argv[1], strategy)

