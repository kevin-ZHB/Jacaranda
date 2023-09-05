# Introduction

# Knowledge

What kinds of the knowledge will we use?

Qunat:

三领域的知识 (importance)

1. Coding
2. Math
3. Finance

## Coding

* Coding language: 
  * **Quantitative Analyst**: `Python` (Developing the trading strategy)
  * Quantitative Developer: C++, C#, Java (Help deploy the trading strategies)

### Level 1: 具备正常coding 的技能

```python
a = 5
def myfunc(a):
  a = 6
  return a

myfun(a)
a = ?
```

### Level 2:  具备看懂高级代码的能力（求职到这个层次）

```python
class MyClass():
  
  def __init__(self):
    pass
  
  def mymethod(self):
    pass
  
  def mymethod2():
    pass
  
  @abstractmethod
  @property
  def mymethod3(self):
    pass
 
```

### Level 3: 看懂源码（工作之后）

```python
# Backtrader
class MetaBase(type):
    def doprenew(cls, *args, **kwargs):
        return cls, args, kwargs

    def donew(cls, *args, **kwargs):
        _obj = cls.__new__(cls, *args, **kwargs)
        return _obj, args, kwargs

    def dopreinit(cls, _obj, *args, **kwargs):
        return _obj, args, kwargs

    def doinit(cls, _obj, *args, **kwargs):
        _obj.__init__(*args, **kwargs)
        return _obj, args, kwargs

    def dopostinit(cls, _obj, *args, **kwargs):
        return _obj, args, kwargs

    def __call__(cls, *args, **kwargs):
        cls, args, kwargs = cls.doprenew(*args, **kwargs)
        _obj, args, kwargs = cls.donew(*args, **kwargs)
        _obj, args, kwargs = cls.dopreinit(_obj, *args, **kwargs)
        _obj, args, kwargs = cls.doinit(_obj, *args, **kwargs)
        _obj, args, kwargs = cls.dopostinit(_obj, *args, **kwargs)
        return _obj

```

## Math

能用数学的语言去描述一个问题。例如：通过数学的语言去描述 What is the trailing stop loss？

![image-20230902224218662](./assets/image-20230902224218662.png)

## Finance

* What is the alpha? beta? sigma?
* black schole model

# Tools

* Python
  * ccxt （数据）
  * Backtrader (回测)
  * ccxt （trading）
  * Database
  * Machine Learning / NN
  * Virtual Machine
* Server
  * AWS
  * GCP
  * 腾讯云、阿里云
* Tools
  * Docker
  * Zotero (文献)
  * Bash

### QA

* ML用的少是因为应用层面，还是技术层面？

懂quant的人不懂技术，懂技术的人做不了quant



* 工作压力大吗？

很大

# 交易策略

## Long-Short

风险敞口是非中性的，收益与市场的上涨下跌相关。

## Arbitrage

position is natural，收益不与市场上涨下跌相关，只与市场的volatility 相关



