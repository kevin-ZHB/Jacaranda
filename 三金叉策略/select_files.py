# -*- coding: gbk -*-

import pandas as pd
import os





def get_file_name(path):

    list_name = []
    for file in os.listdir(path):
        list_name.append((file,os.path.join(path, file)))
    return(list_name[1:-1])

def cal_MAVOL(df):

    num_row = len(df)
    MAVOL5 =[] 
    MAVOL10 = []
    MAVOL = []
    for row in range(num_row):
        if row+10 < num_row:
            mavol5 = sum(df[row:row+5]["成交量"])/5
            mavol10 = sum(df[row:row+10]["成交量"])/10
        else:
            mavol5 = None
            mavol10 = None

        MAVOL5.append(mavol5)
        MAVOL10.append(mavol10)
    
    for row in range(num_row):
        if row+11 < num_row:
            if MAVOL5[row] < MAVOL10[row] and MAVOL5[row+1] >= MAVOL10[row+1]:

                MAVOL.append(-1)
            elif MAVOL5[row] > MAVOL10[row] and MAVOL5[row+1] <= MAVOL10[row+1]:

                MAVOL.append(1)
            else:
                MAVOL.append(None)
        else:
            MAVOL.append(None)
    

    return MAVOL

def select_files(bourse):
    files = get_file_name(bourse)
    last_day = "2022-09-02"
    first_day = "2012-09-02"

    for file_name, path in files:
        df = pd.read_csv(path, encoding="gbk")[["交易日期","开盘价","最高价","最低价","收盘价","成交量","MA金叉死叉","MACD_金叉死叉"]]
        print(df["交易日期"][0], df["交易日期"][0] == last_day)
        print(df["交易日期"][len(df)-1], df["交易日期"][len(df)-1] <= first_day)
        print("--------")

        
        if df["交易日期"][0] == last_day and df["交易日期"][len(df)-1] <= first_day :
            
            MAVOL = cal_MAVOL(df)
            df.insert(6,"openinterest",0,True)
            df.insert(9,"mavol5_overmavol10",MAVOL,True)
            change_content(df)
            df.insert(10,"plate",'a',True)

            df.columns = ['datetime','open','high','low','close','volume','openinterest','ma5_over_ma10','dif_over_dea','mavol5_over_mavol10','plate']

            if bourse == 'Shanghai':
                path = os.path.join("sh", file_name)
            if bourse == "Shenzhen":
                path = os.path.join("sz", file_name)
            df = df.iloc[::-1]
            
            df.to_csv(path, encoding = 'utf-8', index = False)
            
def change_content(df):
    num_row = len(df)

    for i in range(num_row):
        if not pd.isna(df.loc[i,"MA金叉死叉"]) :
            if "5日、10日均线金叉" in df.loc[i,"MA金叉死叉"]:
                df.loc[i,"MA金叉死叉" ] = 1
            elif "5日、10日均线死叉" in df.loc[i,"MA金叉死叉"]:
                df.loc[i,"MA金叉死叉" ] = -1
            else:
                df.loc[i,"MA金叉死叉" ] = None

        if not pd.isna(df.loc[i,"MACD_金叉死叉"]) :
            if "金叉" in df.loc[i,"MACD_金叉死叉"]:
                df.loc[i,"MACD_金叉死叉"] = 1
            elif "死叉" in df.loc[i,"MACD_金叉死叉"]:
                df.loc[i,"MACD_金叉死叉"] = -1

    return



select_files("Shanghai")