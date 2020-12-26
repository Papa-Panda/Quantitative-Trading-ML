import csv
import pandas as pd
import numpy as np
import math
import scipy.stats
import matplotlib.pyplot as plt
import time

def digit_index(temp):
    for n in range(len(temp)):
        if not temp[n].isalpha():
            return n
        
def label_return(ret, threshold):
    if ret > threshold:
        return 1
    elif ret < -threshold:
        return -1
    else:
        return 0

def data_reading( csvfile ):
    b = pd.read_csv( csvfile , sep = '\t')
    b = b.drop( ['ID'] ,1)
#     b.columns = ['ID', 'InstrumentID', 'ExchTime', 'OpenPrice', 'HighPrice', 'LowPrice', 'ClosePrice', 'OpenInterest', 'Turnover', 'Volume']
    time_series = []
    b['InstrumentID'] = b['InstrumentID'].apply(lambda x: x[0] + '_' + x[digit_index(x):digit_index(x)+4])
    b['ExchTime'] = b['ExchTime'].apply(lambda x: pd.to_datetime(x[:len('2014-02-28 08:59:00')] ) )
    time_series = []
    for i in range( len(b) ):
        if len(time_series) == 0 or  b['ExchTime'][time_series[-1]] <  b['ExchTime'][i]:
            time_series += [i]
    return b, time_series

# old
# def data_reading( csvfile ):
#     b = pd.read_csv( csvfile , sep = '\t')
#     b = b.drop( ['ID'] ,1)
#     b.columns = ['ID', 'ExchangeID', 'InstrumentID', 'ExchTime', 'OpenPrice', 'HighPrice', 'LowPrice', 'ClosePrice', 'SettlementPrice', 'OpenInterest', 'Turnover', 'Volume']
#     time_series = []
#     b['InstrumentID'] = b['InstrumentID'].apply(lambda x: x[0] + '_' + x[digit_index(x):digit_index(x)+4])
# #     b['ExchTime'] = b['ExchTime'].apply(lambda x: pd.to_datetime(x[:len('2014-02-28 08:59:00')] ) )
#     for i in range( len(b) ):
#         if len(time_series) == 0 or date_compare( b['ExchTime'][time_series[-1]],  b['ExchTime'][i] ):
# #         if len(time_series) == 0 or  b['ExchTime'][time_series[-1]] <  b['ExchTime'][i]:
#             time_series += [i]
#     return b, time_series

def data_reading_1(csvfile):
    begin = time.time()
    b,time_series = data_reading(csvfile)
    temp = sorted( set(b['ExchTime']) )
    print(len(temp))
    print('Time consumed in data_reading_1',time.time() - begin )
    return b

# get the roll date:
def func1(b,name):
    res = pd.DataFrame() 
    month_dict = {1:[9,10,11,12],5:[1,2,3,4],9:[5,6,7,8]}
    # month_dict = {1:[8,9,10,11],5:[12,1,2,3],9:[4,5,6,7]}
    roll_date = []
    for i in [12,13,14,15,16,17,18]:
        for j in [1,5,9]:
            id = name+'_'+(str(i) + '0' + str(j))
            if j != 1:
                roll_date.append( min( b [ b['ExchTime']> '20'+str(i)+'-0'+str(j) ]['ExchTime'] ).date() )
                temp = b[b['InstrumentID'] == id][b['ExchTime'] > '20'+str(i)+'-0'+str(month_dict[j][0]) ][b['ExchTime'] < '20'+str(i)+'-0'+str(j) ]
            if j == 1:
                temp = b[b['InstrumentID'] == id][b['ExchTime'] > '20'+str(i-1)+'-0'+str(month_dict[j][0]) ][b['ExchTime'] < '20'+str(i)+'-0'+str(j) ]
                roll_date.append( min( b [ b['ExchTime']> '20'+str(i)+'-0'+str(j) ]['ExchTime'] ).date() )
            print(id,len(temp))
    #         ax = temp.plot(x='ExchTime',y='Volume',title = id)
            res = pd.concat([res,temp])
    return res, roll_date

def func2_2_v2(res):
    all_date = sorted( set( [ n.date() for n in set( res['ExchTime'] ) ] ) )
    new_res = pd.DataFrame()
    for date in all_date:
        if all_date.index(date) != len(all_date)-1 :
            next_date = all_date[all_date.index(date) + 1]
#             temp = res[res['ExchTime'] > str(date)][res['ExchTime'] < str(next_date)][['ExchTime','ClosePrice']]
            temp = res[res['ExchTime'] > str(date)][res['ExchTime'] < str(next_date)]
        else:
#             temp = res[res['ExchTime'] > str(date)][['ExchTime','ClosePrice']]
            temp = res[res['ExchTime'] > str(date)]
        temp2 = temp.set_index('ExchTime').resample('60S').ffill()
        concat1 = pd.DataFrame(index = pd.date_range(str(date) + ' 08:59:00',str(date) + ' 10:14:00', freq='60S'))
        concat1_5 = pd.DataFrame(index = pd.date_range(str(date) + ' 10:30:00',str(date) + ' 11:29:00', freq='60S'))
        concat2 = pd.DataFrame(index = pd.date_range(str(date) + ' 13:30:00',str(date) + ' 14:59:00', freq='60S'))
        df2 = pd.concat([concat1,concat1_5,concat2])
        df3 = pd.merge(df2, temp2, left_index = True, right_index = True, how = 'left') 
        df3.ffill()
        df3 = df3.fillna(method = 'bfill')
        df3 = df3.fillna(method = 'ffill')
        
        if str( date )[-1:] == '2':
            print(date, len( temp) , len( temp2 ) ,  len(concat1),len(concat2),len( df2),len(df3) )
        new_res = pd.concat([new_res,df3])
        # this part is added to the next connection
#         new_res['ExchTime'] = new_res.index
#         new_res.index = range(len(new_res))
    return new_res

def get_rolled_closeprice(res,roll_date):
#     res3 = pd.DataFrame.copy( res[[ u'ExchTime','ClosePrice']] )
    res3 = pd.DataFrame.copy( res )
    roll_date_temp = list( pd.Series( roll_date ).drop_duplicates() )
    for date in roll_date_temp[1:-1]:
#         print(date)
        if  len ( res3[ res3['ExchTime'] < str( date ) ] ) < 1 :
            continue
        roll_open = res3[ res3['ExchTime'] > str( date ) ]['OpenPrice'].iloc[0]
        last_close = res3[ res3['ExchTime'] < str( date ) ]['ClosePrice'].iloc[-1]
        print( date,res3[ res3['ExchTime'] > str( date ) ]['ClosePrice'].iloc[0] )
        n = len(res3[ res3['ExchTime'] < str( date ) ])
        m = len(res3[ res3['ExchTime'] > str( date ) ])
        res3['ClosePrice'] -= [0] * n + [ - (roll_open - last_close) ] * m 
        res3['OpenPrice'] -= [0] * n + [ - (roll_open - last_close) ] * m 
        res3['HighPrice'] -= [0] * n + [ - (roll_open - last_close) ] * m 
        res3['LowPrice'] -= [0] * n + [ - (roll_open - last_close) ] * m 
        
        print( date, res3[ res3['ExchTime'] > str( date ) ]['ClosePrice'].iloc[0] )
    return res3

