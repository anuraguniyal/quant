import sys
import os
import csv
import datetime
import argparse

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
    def __init__(self):
        self.total_profit = 0
        self.total_premium = 0

    def add_day(self, day):
        pass

    def report(self):
        print("profit: {} premium: {} net: {} return: {:.2f}%".format(
                    self.total_profit, self.total_premium, self.profit()
                    , self.profit()*100/self.total_premium))

    def profit(self):
        return self.total_profit - self.total_premium

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
        premium is in percent, so it makes sense with historical data
        """
        super().__init__()
        self.strike_down = strike_down
        self.expiry_days = expiry_days
        if premium is None:
            self.premium = calculate_premium(strike_down, expiry_days)
        else:
            self.premium = premium
        self.puts = []

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


def simulate(history, strategy):
    for row in history:
        day = Day.from_row(row)
        strategy.add_day(day)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Calculate premium or profi')
    parser.add_argument('--days', type=int, help='expiry days for PUT including today', required=True)
    parser.add_argument('--premium', type=float, help='whats the premiunm')
    parser.add_argument('--stock', type=str, help='Stock ticker', default='SPY')
    parser.add_argument('--down', type=float, help='How much strike is down compared to current price.', required=True)

    args = parser.parse_args()
    stock_file = args.stock+'.csv'
    if not os.path.exists(stock_file):
        parser.error(f"Stock {args.stock} doesn't have a csv files")

    with open(stock_file) as csv_file:
        reader = csv.reader(csv_file)
        history = list(reader)[1:]

    # lets take last valus as current price and calculate premium from there
    day_rates = Day.from_row(history[-1])

    if args.premium is not None:
        premium_percent = args.premium*100/day_rates.open
        strategy = BuyPutStrategy(args.down, args.days, premium_percent)
        simulate(history, strategy)
        strategy.report()
    else:
        # calculate break even premium
        # assume premium from 0 to 2%
        max_per = 2
        mul = 1000
        for i in range(max_per*mul):
            premium_percent = i/mul
            strategy = BuyPutStrategy(args.down, args.days, premium_percent)
            simulate(history,  strategy)
            if(strategy.profit()<0):
                break
            premium = premium_percent*day_rates.open/100
            print(f"Premium {premium} profit: {strategy.profit()}")


