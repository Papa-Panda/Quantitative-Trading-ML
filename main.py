'''
Created on Nov 25, 2017

@author: jun
'''
import json
import pandas as pd
from bs4 import BeautifulSoup
import numpy as np
import time
import os
import matplotlib.pyplot as plt
from datetime import datetime
from datetime import timedelta
import pickle

from utils import Raw_Data_to_Minute_Data, Resample_Minute_Data
from utils import CalcDI, CalcIndicators, CalcPnL_MarketOrder, SummarizeStrategy_Daily
from utils import Display_Strategy
from utils import CalcSmoothPar, TradingSignalGraphics

from strategy import pairs_trading


freq = '5T'
initial_capital = 5000
trade_unit = 1
fee = 0.003

eth_minute_data = Raw_Data_to_Minute_Data('ETH')
btc_minute_data = Raw_Data_to_Minute_Data('BTC')

eth_resampled_data = Resample_Minute_Data(eth_minute_data.iloc[(-500000) : ], freq)
#print(eth_resampled_data.columns)
btc_resampled_data = Resample_Minute_Data(btc_minute_data.iloc[(-500000) : ], freq)

btc, eth = pairs_trading(btc_resampled_data[-12000:],eth_resampled_data[-12000:], 1 )

# def check():
#     n = btc.shape[0]
#     ratio = btc['close_price'].values/eth['close_price'].values
#     mean = np.mean(ratio)
#     std = np.std(ratio)
#     #plt.plot(range(n), btc['close_price']/np.max( btc['close_price'].values ))
#     #plt.plot(range(n), eth['close_price']/np.max( eth['close_price'].values ))
#     plt.plot(range(n), ratio)
#     plt.plot(range(n), btc['trading_signal']+10)
#     plt.plot(range(n), np.ones(n) * (mean + std))
#     plt.plot(range(n), np.ones(n) * mean)
#     plt.plot(range(n), np.ones(n) * (mean - std))
#     plt.show()
# 
# 
#     
btc = CalcPnL_MarketOrder(btc, initial_capital, trade_unit, fee)
(annual_return, max_drawdown, Sharpe_ratio, Strategy_1_Daily) = SummarizeStrategy_Daily(btc)
print((annual_return, max_drawdown, Sharpe_ratio))
 
eth = CalcPnL_MarketOrder(eth, initial_capital, 15, fee)
(annual_return, max_drawdown, Sharpe_ratio, Strategy_1_Daily) = SummarizeStrategy_Daily(eth)
print((annual_return, max_drawdown, Sharpe_ratio))
