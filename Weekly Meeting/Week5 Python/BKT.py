import pandas as pd
import datetime
import chinese_calendar
from pprint import pprint as pp
from matplotlib import pyplot


class BKT:
    timeline = None
    mode = 1
    initial_fund = 100000
    commission = 0
    hands = 1
    data = None
    hands_mode = False

    def __init__(self):
        self.Setter = self.Setter(self)
        self.Tester = self.Tester(self)
        #self.Plotter = self.Plotter(self)

    class Setter():
        def __init__(self, out):
            self.out = out

        def set_timeline(self, start_str, end_str):
            '''
            start_str & end_str : string format : '%Y%m%d'
            return : dataframe of all working days
            '''
            start = datetime.datetime.strptime(
                start_str, '%Y%m%d')  # 将字符串转换为datetime格式
            end = datetime.datetime.strptime(end_str, '%Y%m%d')
            # 获取指定范围内工作日列表
            lst = chinese_calendar.get_workdays(start, end)
            for time in lst:
                if time.isoweekday() == 6 or time.isoweekday() == 7:
                    lst.remove(time)  # 将周六周日排除出交易日列�?
            self.out.timeline = pd.to_datetime(
                pd.Series([item.strftime('%Y%m%d') for item in lst]))
            return self.out.timeline

        def set_mode(self, mode):
            self.out.mode = mode

        def set_fund(self, fund):
            self.out.fund = fund

        def set_commission(self, commission):
            self.out.commission = commission

        def set_hands(self, hand):
            self.out.hands = hand

        def set_hands_mode(self, mode):
            self.out.hands_mode = mode

        def __data_fitting(self, data, timeline):
            ''' 
                input �?
                    data�?  list of all dataframe
                    timeline�? output of set_timeline(start,end)
                output:
                    {date: all stock info at this date as pd}
            '''
            mix = pd.concat(data)
            return {date: mix[mix.time == date].reset_index().drop(columns=['index', 'time']) for date in timeline}

        def set_data(self, data):
            ''' 
                input:
                    data:  list of all dataframe
                    timeline: output of set_timeline(start,end)
                output:
                    see user guide
            '''
            adjusted_data = self.__data_fitting(data, self.out.timeline)
            self.out.data = adjusted_data

    class Tester():
        def __init__(self, out):
            self.out = out

        def __initial(self):
            record = pd.DataFrame(columns=[
                                  'date', 'name', 'code', 'type', 'price', 'amount', 'state'])     # 对账�? 作为df记录每日交易
            holding = pd.DataFrame(
                columns=['name', 'code', 'cost', 'amount', 'profit', 'period'])  # 持仓�? 作为df更新每日持仓变化
            trading_plan = pd.DataFrame(
                columns=['name', 'code', 'type', 'price', 'amount'])      # 计划�? 作为df更新每日的交易计划变�?
            account = {'initial': self.out.initial_fund, 'total_asset': self.out.initial_fund, 'available_asset': self.out.initial_fund,'profit': 0}  # 总账�? 作为dict更新账户的信�?
            hist = pd.DataFrame([[self.out.timeline[0], self.out.initial_fund, self.out.initial_fund, 0]], columns=['date', 'available', 'total', 'profit'])  # 账户历史 以每笔交易为单位
            trading_plans = {}
            fail_trades = pd.DataFrame(
                columns=['date', 'name', 'code', 'type', 'price', 'amount', 'reason'])
            daily_hist = pd.DataFrame(
                columns=['date', 'available', 'total', 'profit'])  # 账户历史  作为df记录每日账户变化
            return record, holding, trading_plan, account, hist, trading_plans, daily_hist, fail_trades,

        def __update(self, plan, date, holding):
            '''
            :param holding:
            :return:
            :param plan: DataFrame(index)
            :param date: datetime
            :return: change_
            '''

            if plan.type == 'sell':
                hd = holding.loc[plan.code == holding.code]
                if hd.empty == True:
                    return None
                if len(hd.index) > 1:
                    return None
                if self.out.hands_mode:
                    number = plan.amount
                else:
                    # 1. 任何变量不能为空�? 2. 任何数量不能超过1
                    number = int(hd.amount * plan.amount)
                if number != 0:  # 保证交易的发�?
                    money_change = number * plan.price * \
                        (1 - self.out.commission)*self.out.hands
                    profit = number*self.out.hands * \
                        (plan.price - float(hd.cost)) * \
                        (1 - self.out.commission)
                    state = '卖出'
                    if plan.amount == 1:
                        state = '平仓'

                    holding.loc[holding.code == plan.code] = [plan['name'], hd.code, hd.cost, int(hd.amount) -number, profit, int(hd.period)]
                    self.out.account['total_asset'] += profit
                    self.out.account['available_asset'] += money_change
                    self.out.account['profit'] = (
                        self.out.account['total_asset'] - self.out.initial_fund)
                    self.out.hist.loc[len(self.out.hist.index)] = [
                        date, self.out.account['available_asset'], self.out.account['total_asset'], self.out.account['profit']]

                    self.out.record.loc[len(self.out.record.index)] = [date, plan['name'], plan.code, plan.type, plan.price, number,
                                                                       state]
                else:
                    self.out.fail_trades.loc[len(self.out.fail_trades.index)] = [
                        date, plan.name, plan.code, plan.type, plan.price, plan.amount, 'selling ratio mistake']

            elif plan.type == 'buy':
                if self.out.hands_mode:
                    count = plan.amount
                else:
                    count = int(self.out.account['available_asset'] * plan.amount / (
                        (1 + self.out.commission) * plan.price) / self.out.hands)  # 手数
                if count != 0:
                    commission_ = count*self.out.hands * plan.price * self.out.commission
                    cost = count*self.out.hands * plan.price + commission_  # 总共花了多少�?
                    self.out.account['total_asset'] -= commission_
                    self.out.account['available_asset'] -= cost
                    self.out.account['profit'] = (
                        self.out.account['total_asset'] - self.out.initial_fund)
                    self.out.hist.loc[len(self.out.hist.index)] = [date, self.out.account['available_asset'], self.out.account['total_asset'], self.out.account['profit']]
                    if plan.code in holding.code.values:
                        current = holding.loc[holding.code == plan.code]
                        cc = current.cost * current.amount / (current.amount + count) + cost / count/self.out.hands * count / (
                            current.amount + count)

                        holding.loc[holding.code == plan.code, 'name':'period'] =pd.DataFrame([plan['name'], plan.code, cc, current.amount+ count, current.profit - commission_, current.period])
                        state = '加仓'

                    else:
                        holding.loc[len(holding.index)] = [
                            plan['name'], plan.code, cost/count/self.out.hands, count, -commission_, 0]
                        state = '建仓'
                    self.out.record.loc[len(self.out.record.index)] = [
                        date, plan['name'], plan.code, plan.type, plan.price, count, state]
                else:
                    self.out.fail_trades.loc[len(self.out.fail_trades.index)] = [date, plan.name, plan.code, plan.type,plan.price, plan.amount,'available asset is not enough']

        def test(self, cls):
            self.out.record, self.out.holding, self.out.trading_plan, self.out.account, self.out.hist, self.out.trading_plans, self.out.daily_hist, self.out.fail_trades = self.__initial()
            for date in core.timeline:
                today = core.data[date]
                trading_plan = self.out.trading_plan
                for index in trading_plan.index:
                    plan = trading_plan.loc[index]
                    stock = today.loc[plan.code == today.code]
                    if stock.empty != True:
                        if (plan.type == 'sell' and plan.price <= int(stock.high)) or (
                                plan.type == 'buy' and plan.price >= int(stock.low)):
                            self.__update(plan, date, self.out.holding)
                        else:
                            self.out.fail_trades.loc[len(self.out.fail_trades.index)] = [
                                date, plan.name, plan.code, plan.type, plan.price, plan.amount, 'price out of range']
                    else:
                        self.out.fail_trades.loc[len(self.out.fail_trades.index)] = [date, plan.name, plan.code, plan.type, plan.price, plan.amount, 'stock not trade today']
                self.out.trading_plans[date] = self.out.trading_plan
                self.out.trading_plan = pd.DataFrame(
                    columns=['name', 'code', 'type', 'price', 'amount'])
                self.out.holding = self.out.holding.loc[self.out.holding.amount != 0]
                self.out.holding.period += 1

                ''' 每日账户数据更新计算流程 待完�? '''
                self.out.daily_hist.loc[len(self.out.daily_hist.index)] = [date, self.out.account['available_asset'], self.out.account['total_asset'], self.out.account['profit']]
                if self.out.mode == 1:
                    self.out.trading_plan = cls(self.out, today, date).final()
                else:
                    self.out.trading_plan = cls(
                        self.out, self.out.data, date).final()
            # self.out.holding,self.out.trading_plan = self.td()
            self.out.record.to_csv('对账单.csv')
            self.out.hist.to_csv('账户变更.csv')
            self.out.daily_hist.to_csv('每日账户变更.csv')


class Strategy():
    def __init__(self, core, data, date):
        '''
        :param core: BKT itself
        :param data: 取决于mode，如果为1 那么就是 Dataframe(stock)
                                如果为2 那么就是 { datetime : Dataframe(stock) }
        :param date: 日期
        '''
        self.core = core
        self.data = data
        self.date = date
        self.trading_plan = pd.DataFrame(
            columns=['name', 'code', 'type', 'price', 'amount'])

    def sell(self):
        for index in self.core.holding.index:
            stock = self.core.holding.loc[index]
            # pp(stock.name)
            if stock.period <= 7:
                self.trading_plan.loc[len(self.trading_plan.index)] = [
                    stock['name'], stock.code, 'sell', round(1.01*float(stock.cost), 2), 0.5]
            if stock.period > 10:
                self.trading_plan.loc[len(self.trading_plan.index)] = [stock['name'], stock.code, 'sell', round(float(self.data.loc[self.data.code == stock.code].low), 2), 0.5]

    def buy(self):
        data = self.data.loc[self.data.change >= 1.01]
        # print(data)
        for index in data.index:
            # print(index)
            stock = data.loc[index]
            # print(stock)
            # pp(stock['name'])
            self.trading_plan.loc[len(self.trading_plan.index)] = [stock['name'], stock.code, 'buy', stock.close, 0.2]

    def final(self):
        self.data['change'] = self.data.high/self.data.low
        self.sell()
        self.buy()
        # print(self.trading_plan)
        return self.trading_plan


def reader(filepath):
    output = []
    for file in filepath:
        df = pd.read_csv(file, encoding='gbk').rename(columns={
            '交易日期': 'time', '最高价': 'high', '最低价': 'low', '股票代码': 'code', '股票名称': 'name', '开盘价': 'open', '收盘价': 'close'})
        df.time = pd.to_datetime(df.time)
        df = df.loc[:, ['time', 'code', 'name',
                        'open', 'close', 'high', 'low']]
        output.append(df)
    return output


core = BKT()
setter = core.Setter
tester = core.Tester
setter.set_timeline('20200101', '20210101')
setter.set_hands(100)
setter.set_commission(0.001)
# pp(core.timeline)
# sample data of timeline
setter.set_data(reader(['./sh{}.csv'.format(i)
                for i in range(600000, 600005)]))
# pp(core.data)
tester.test(Strategy)
# print(core.hist.set_index('date').profit)
ts = core.hist.set_index('date').profit
ts.plot()
