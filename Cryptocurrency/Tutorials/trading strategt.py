import ccxt
import pandas as pd
from typing import List, Dict, Tuple, Sequence, TypeVar, Any
import datetime as dt



# Step 1: Obtaining the data
    
    
def obtain_data(symbol = 'BTC/USDT', timeframe = '1d', limit = 1000) -> pd.DataFrame:
    
    
    exchange_name = 'binanceus'
    exchange = eval('ccxt.%s()' % exchange_name)
    # exchange.set_sandbox_mode(True) # set to True for sandbox environment if you have applied the sandbox api, all the money will be fake! if you set to False, it will be real money!
    exchange.load_markets()
    exchange.verbose = False  # enable verbose mode after loading the markets
    
    price = exchange.fetchOHLCV(symbol='BTC/USDT', timeframe='1d', limit=1000)
    price = pd.DataFrame(price, columns=['time', 'open', 'high', 'low', 'close', 'volume'])
    price['time'] = pd.to_datetime(price['time'], unit='ms')
    price.set_index('time', inplace=True)
    print(price.info())
    
    return price

# Step 2: Defining the trading strategy

"""
    EMA_A = 20
    EMA_B = 50
    
    We in the market when the EMA_A is above the EMA_B and we are out of the market when the EMA_A is below the EMA_B.
"""

# Step 3: Backtesting the trading strategy

import backtrader as bt

class MyDataFeed(bt.feeds.PandasData):
    # add one more columns called quote
    lines = ('quote',)

    params = (
        ('datetime', -1),
        
        ('open', 0),
        ('high', 1),
        ('low', 2),
        ('close', 3),
        ('volume', 4),
        ('quote', -1),
    )



# Strategy class template 
class JacarandaStrategy(bt.Strategy):
    params = (
        ('short_window', 20),  # Short-term EMA period
        ('long_window', 50),   # Long-term EMA period
    )

    def log(self, txt, dt=None):
        ''' Logging function for this strategy'''
        dt = dt or self.datas[0].datetime.datetime(0)
        print('%s, %s' % (dt, txt))

    def __init__(self):
        # Add a EMA indicator
        self.dataclose = self.datas[0].close
        self.ema_a = bt.talib.EMA(self.dataclose, timeperiod=self.params.short_window,plotname = 'ema_a',)
        self.ema_b = bt.talib.EMA(self.dataclose, timeperiod=self.params.long_window,plotname = 'ema_b',)
        
        self.order = None

    def next(self):
    
        self.log(f'Close: {self.dataclose[0]}, EMA_a: {self.ema_a[0]},EMA_b: {self.ema_b[0]} ,Cash: {self.broker.getcash()}, Value: {self.broker.getvalue()}')
        
        if self.order:
            return
                
        ########################################## Long Only ##########################################
        # Out the market
        if not self.position:
            if self.ema_a[0] >= self.ema_b[0]:
                
                self.log('BUY CREATE, %.2f' % self.dataclose[0])
                self.order = self.buy()

        # In the market
        else:
            # if self.dataclose[0] < self.sma[0]:
            if self.ema_a[0] <= self.ema_b[0]:
                self.log('SELL CREATE, %.2f' % self.dataclose[0])
                
                # Keep track of the created order to avoid a 2nd order
                self.order = self.close()

    def notify_order(self, order):
        
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))
                
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
                
            else : # Sell
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Write down: no pending order
        self.order = None
        
   
    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))     
 
 
# Real trading
    while 1 != 0:
        if signal == 'buy':
            your_account.buy()
            
        elif signal == 'sell':
            your_account.sell()
    



if __name__ == '__main__':

    # data = obtain_data()
    # print(data.head())
    
    cerebro = bt.Cerebro() # default observers: Broker,traders
    cerebro.broker.setcash(100000.0)
    cerebro.addstrategy(JacarandaStrategy)
    cerebro.broker.setcommission(commission=0.001)
    df_data = obtain_data()
    data = MyDataFeed(dataname = df_data)
    cerebro.adddata(data)
    
    cerebro.run()
    
    cerebro.plot()
    
    
    
    
    


 