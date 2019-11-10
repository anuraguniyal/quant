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
        return Day(date, float(row[1]), float(row[4]), float(row[2]), float(row[3]))

class Put:
    def __init__(self, expiry, strike, premium):
        self.expiry = expiry
        self.strike = strike
        self.premium = premium
        self.sold = False
        self.profit = 0

    def sell(self, day):
        if self.sold:
            raise ValueError("already sold")
        self.sold = True
        # assume we sell at close
        if self.strike > day.close:
            self.profit = self.strike - day.close

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
    def __init__(self, strike_down, expiry_days, premium=None):
        """
        strike_down: precent below current price at which we buy put
        expiry_days: in how many days put expires
        """
        self.strike_down = strike_down
        self.expiry_days = expiry_days
        if premium is None:
            self.premium = calculate_premium(strike_down, expiry_days)
        else:
            self.premium = premium
        self.puts = []
        self.total_profit = 0
        self.total_premium = 0

    def add_day(self, day):
        # sell any put expiring today
        for put in self.puts:
            if put.expiry == day.date:
                put.sell(day)
                self.total_profit += put.profit
                self.total_premium += put.premium

        # buy put
        # we assume we buy put at open
        expiry = day.date+datetime.timedelta(self.expiry_days)
        strike = day.open*(1 - self.strike_down/100)
        premium = day.open*self.premium/100
        put = Put(expiry, strike, premium)
        self.puts.append(put)

    def profit(self):
        return self.total_profit - self.total_premium

def simulate(csv_path, strategy):
    with open(csv_path) as csv_file:
        reader = csv.reader(csv_file)
        for i, row in enumerate(reader):
            if i == 0:
                continue # skip header
            day = Day.from_row(row)
            strategy.add_day(day)
            print("{}: profit: {} premium: {} net: {}".format(
                    day.date, strategy.total_profit, strategy.total_premium, strategy.profit()))


strategy = BuyPutStrategy(5, 5,.013)

simulate(sys.argv[1], strategy)

