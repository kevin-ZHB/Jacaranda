import random
signals = ['buy', 'sell'] * 10

random.shuffle(signals)

current_time = 20220101

for sig in signals:
    if sig == 'buy':
        print(current_time,'buy')
        
    elif sig == 'sell':
        print(current_time,'sell')
        
    current_time += 1
