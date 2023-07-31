import tkinter as tk
from tkinter import *
from PIL import Image,ImageTk
from pprint import pprint
import random as r
from time import sleep
import time
import threading

def reset():
    global gifts,g
    gifts = {"墨大水晶球": {"prob": 0, "count": 0, "total": 1},
            "墨大周边公仔": {"prob": 0.002, "count": 5, "total": 5},
            "小鲨鱼": {"prob": 0.002, "count": 2, "total": 2},
            "马克杯": {"prob": 0.01, "count": 7, "total": 7},
            "桌面绿植": {"prob": 0.02, "count": 10, "total": 10},
            "北欧香薰": {"prob": 0.1, "count": 30, "total": 35},
            "奶茶": {"prob": 0.35, "count": 60, "total": 220},
            "抽李阳一巴掌": {"prob": 0.5, "count": 500, "total": 500}}
    g = []
    for k, v in gifts.items():
        g += [k]*v['count']
    return g

def main_page(default):
    global gifts
    positions = [(1, 1), (1, 2), (1, 3), (2, 3), (3, 3), (3, 2), (3, 1), (2, 1)]
    for pos,name in zip(positions,default.keys()):
        default[name]['pos'] = pos

    gifts = default.copy()
    # 主界面设置
    main = Tk()
    main.title('Jacaranda 抽奖程序')
    main.geometry('600x500')

    # 主界面按钮设置
    front = Button(activeforeground = 'red',bg='white',text = '抽奖界面',height = 10,width = 40,command = frontpage).pack()
    back = Button(activeforeground = 'red',bg='white',text = '后台界面',height = 10,width = 40,command = backpage).pack()
    tk.mainloop()
def backpage():
    global entries
    def get_entry():
        for key in gifts.keys():
            gifts[key]['prob'] = float(gifts[key]['entry'].get())
        print('当前概率分布为:')
        pprint([name+':'+str(gifts[name]['prob']) for name in gifts.keys()])
    back = Toplevel()
    back.title('后台界面')
    back.geometry('400x550')

    Button(back,activeforeground='red', bg='white', text='修改', height=5, width=18, command=get_entry).grid(row=9, column=3)
    for name in gifts.keys():
        pos = list(gifts.keys()).index(name)
        Label(back,text = name+': ',height = '3',width = '10').grid(row = pos,column = 1)
        e = Entry(back,width = '10')
        e.insert(0,gifts[name]['prob'])
        gifts[name]['entry'] = e
        e.grid(row=pos,column =2 )

def frontpage():
    global labels,positions,click
    def create_label(main,text,pos,bg = 'deepskyblue',image = None):
        return Label(main,bg = bg,height = '5',width = '17',text = text,justify =pos,borderwidth = 3,image = image,font = ('黑体',50))

    def get_final():
        result = r.choice(g)
        g.remove(result)
        for i in gifts:
            if gifts[i]['prob'] == 1:
                return i
        return result

    def turn():
        # 全转盘轮动规则 - 随机闪动 - click变会标为数字 数字随机闪动
        ranpick()
        final = get_final()
        shine(gifts[final]['label'], 1.0)
        shine(gifts[final]['label'], True,'darkred','gold')

    # 抽奖动画
    def ranpick():
        for name in gifts.keys():
            L = gifts[name]['label']
            #L.config(bg = 'deepskyblue')
            L.update()

        speed = [float(i/100) for i in range(10,20,1)]
        for i in speed:
            lucky = r.choice(list(gifts.keys()))
            shine(gifts[lucky]['label'],i)
    def shine(L,t,col = 'gold',fg = 'black'):
        # 指定位置的标签闪动
        L.config(bg = col)
        L.update()
        if type(t) == type(0.1):
            sleep(t)
            L.config(bg = 'deepskyblue',fg = fg)
            L.update()
        else:
            pass
        return L

    back = Toplevel()
    back.title('不lowb的抽奖界面')
    back.geometry('1920x1080')

    bkg = ImageTk.PhotoImage(Image.open('background.gif').resize((1920,1080)))
    background = Label(back,width = 1920,height = 1080, image = bkg,anchor = 'center')
    background.pack()
    positions = []
    for i in [130,700,1265]:
        for j in [68,390,715]:
            if i != 700 or j != 390:
                positions.append((i,j))
    for name,pos in zip(gifts.keys(),positions):
        gifts[name]['pos'] = pos
        L = create_label(back,name,'center')
        gifts[name]['position'] = pos
        gifts[name]['label'] = L
        L.place(x=pos[0],y=pos[1])
    #congra = Label()
    ckg = ImageTk.PhotoImage(Image.open('button2.png').resize((int(760*0.7),int(429*0.7))))
    click = Button(back, command=turn, width=str(int(760*0.7)), height=str(int(429*0.7)),image = ckg,bg = 'darkorange',bd=0,relief = 'flat',activeforeground = 'darkorange')
    click.place(x = 700,y =390)
    tk.mainloop()
reset()
main_page(gifts)


