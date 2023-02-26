
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

from datetime import datetime
import enum
# For datetime objects
import pandas as pd

# Import the backtrader platform
import backtrader as bt

import os


class GenericCSVData_extend(bt.feeds.GenericCSVData):

    # Add a 'pe' line to the inherited ones from the base class
    lines = ('ma5_over_ma10', 'dif_over_dea', 'mavol5_over_mavol10')

    # openinterest in GenericCSVData has index 7 ... add 1
    # add the parameter to the parameters inherited from the base class
    params = (


        ('ma5_over_ma10', 7),
        ('dif_over_dea', 8),
        ('mavol5_over_mavol10', 9),
        ('plate', 10)
    )



# Create a Stratey
class TestStrategy(bt.Strategy):

    params = dict(
        poneplot=False,
    )

    def log(self, txt, dt=None):
        ''' Logging function fot this strategy'''
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        #self.dataclose = self.datas[0].close

        # To keep track of pending orders and buy price/commission
       # Keep a reference to the "close" line in the data[0] dataseries

        self.order = None
        self.inds = dict()
        self.num_loss = 0
        self.num_win = 0
        self.num_trade = 0
        self.takeprofit = 0
        self.stoploss = 0

        for i, data in enumerate(self.datas):
            self.inds[data] = dict()

            ma5_over_ma10 = data.ma5_over_ma10 > 0
            ma5_under_ma10 = data.ma5_over_ma10 < 0

            dif_over_dea = data.dif_over_dea > 0
            dif_under_dea = data.dif_over_dea < 0

            mavol5_over_mavol10 = data.mavol5_over_mavol10 > 0
            mavol5_under_mavol10 = data.mavol5_over_mavol10 < 0

            ma_dea_gold_fork = data.dif_over_dea + data.ma5_over_ma10 == 2
            
            ma_mavol_gold_fork = data.ma5_over_ma10 + data.mavol5_over_mavol10 == 2

            mavol_dea_gold_fork = data.mavol5_over_mavol10 + data.dif_over_dea == 2

            ma_dea_dead_fork = data.dif_over_dea + data.ma5_over_ma10 == -2

            ma_mavol_dead_fork = data.ma5_over_ma10 + data.mavol5_over_mavol10 == -2

            mavol_dea_dead_fork = data.mavol5_over_mavol10 + data.dif_over_dea == -2

            self.inds[data]['buy_sig'] = bt.And(
                ma_dea_gold_fork, ma_mavol_gold_fork, mavol_dea_gold_fork)
            self.inds[data]['sell_sig'] = bt.Or(
                ma_dea_dead_fork, mavol_dea_dead_fork, ma_mavol_dead_fork)

            if i > 0:
                if self.p.poneplot:
                    data.plotinfo.plotmaster = self.datas[0]

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Name:%s, Price: %.2f, Cost: %.2f, Comm: %.2f' %
                    (order.data._name,
                     order.executed.price,
                     order.executed.value,
                     order.executed.comm))

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:  # Sell
                self.log('SELL EXECUTED,Name: %s,  Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.data._name,
                          order.executed.price,
                          order.executed.value,
                          order.executed.comm))

            self.bar_executed = len(self)

        elif order.status in [order.Canceled]:
            self.log('Order Canceled')

        elif order.status in [order.Margin]:
            self.log('Order Margin')

        elif order.status in [order.Rejected]:
            self.log('Order Rejected')

        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return
        self.log('操作利润, 毛利 %.2f, 净利润 %.2f' %(trade.pnl, trade.pnlcomm))
        if trade.pnl > 0:
            self.num_win += 1
        elif trade.pnl < 0:
            self.num_loss += 1

        self.num_trade += 1

        self.log('盈利操作: %d, 亏损操作： %d, 总操作数： %d\n' %
                 (self.num_win, self.num_loss, self.num_trade))

        #self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' % (trade.pnl, trade.pnlcomm))

    def next(self):
        # Simply log the closing price of the series from the reference
        #self.log('Close, %.2f' % self.dataclose[0])

        for i, data in enumerate(self.datas):

            #self.log('当前回测股票: %s' % data._name)
            dt, dn = self.datetime.date(), data._name
            pos = self.getposition(data).size

            if self.order:
                return

            # Check if we are in the market
            if not pos:

                # Not yet ... we MIGHT BUY if ...
                if self.inds[data]['buy_sig'] :
                    #self.log('BUY CREATE, %.2f' % data.close[0])

                    # Keep track of the created order to avoid a 2nd order
                    #size = self.broker.get_cash() / (data.close[0]*1.1)
                    self.buy(data=data, size=100)
                    self.takeprofit = data.close[0] * (1+0.06)
                    self.stoploss = data.close[0] * (1-0.05)
                    #self.log( '全仓买入 %s ， %.2f' % (data._name, size))

            else:

                # Already in the market ... we might sell
                if self.inds[data]['sell_sig'] or data.close[0] >= self.takeprofit or data.close[0] <= self.stoploss:
                    # SELL, SELL, SELL!!! (with all possible default parameters)
                    #self.log('SELL CREATE, %.2f' % data.close[0])

                    # Keep track of the created order to avoid a 2nd order
                    #size = self.position
                    self.close(data=data)


def get_file_name(path):

    list_name = []
    for file in os.listdir(path):
        list_name.append((file, os.path.join(path, file)))

    return (list_name)


if __name__ == '__main__':
    # Create a cerebro entity
    cerebro = bt.Cerebro()

    # Add a strategy
    cerebro.addstrategy(TestStrategy)

    # Datas are in a subfolder of the samples. Need to find where the script is
    # because it could have been called from anywhere

    files = get_file_name('sh')

    print(files[1])

    for file_name, path in files[7:8]:
        # Create a Data Feed
        data = GenericCSVData_extend(
            dataname=path,
            fromdate=datetime(2017, 9, 2),
            todate=datetime(2022, 9, 2),

            nullvalue=0.0,
            dtformat=('%Y-%m-%d'),

        )
        # Add the Data Feed to Cerebro
        cerebro.adddata(data, name=file_name)

    # Set our desired cash start
    cerebro.broker.setcash(100000.0)

    # Set the commission - 0.1% ... divide by 100 to remove the %
    # cerebro.broker.setcommission(commission=0.001)

    # Print out the starting conditions
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())

    # Run over everything
    cerebro.run()
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    print('Final Benefit Value: %.2f' % (cerebro.broker.getvalue() - 100000.0))

    cerebro.plot(iplot = False)

    # Print out the final result
