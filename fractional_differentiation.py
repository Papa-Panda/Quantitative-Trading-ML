import csv
import pandas as pd
import numpy as np
import math
import scipy.stats
import matplotlib.pyplot as plt
# %matplotlib inline
import pprint
    

def getWeights(d,size):
    # thres>0 drops insignificant weights
    w=[1.]
    for k in range(1,size):
        w_=-w[-1]/k*(d-k+1)
        w.append(w_) 
    w=np.array(w[::-1]).reshape(-1,1) 
    return w

def plotWeights(dRange,nPlots,size):
    w=pd.DataFrame()
    for d in np.linspace(dRange[0],dRange[1],nPlots):
        w_=getWeights(d,size=size) 
        w_=pd.DataFrame(w_,index=range(w_.shape[0])[::-1],columns=[d]) 
        w=w.join(w_,how='outer')
    ax=w.plot()
    ax.legend(loc='upper left');plt.show() 
    return

def fracDiff(series,d,thres=.01): 
    '''
    Increasing width window, with treatment of NaNs
    Note 1: For thres=1, nothing is skipped.
    Note 2: d can be any positive fractional, not necessarily bounded [0,1]. 
    '''
    #1) Compute weights for the longest series 
    w=getWeights(d,series.shape[0])
    #2) Determine initial calcs to be skipped based on weight-loss threshold 
    w_=np.cumsum(abs(w))
    w_/=w_[-1]
    skip=w_[w_>thres].shape[0]
    #3) Apply weights to values
    df={}
    for name in series.columns:
        seriesF = series[[name]].fillna(method='ffill').dropna()
        df_ = pd.Series([0] * len(seriesF)) 
        for iloc in range(skip,seriesF.shape[0]):
            loc=seriesF.index[iloc]
            if not np.isfinite(series.loc[loc,name]):continue # exclude NAs 
            df_[loc]=np.dot(w[-(iloc+1):,:].T,seriesF.loc[:loc])[0,0]
        df[name]=df_.copy(deep=True) 
    df=pd.concat(df,axis=1)
    return df

def getWeights_FFD(d, thres, lim):
    w, k = [1.], 1
    ctr = 1
    while True:
        w_ = -w[-1]/k*(d-k+1)
        if abs(w_)<thres:
            break
        w.append(w_)
        k+=1
        ctr += 1
        if ctr == lim:
            break
    w = np.array(w[::-1]).reshape(-1,1)
    return w


def fracDiff_FFD(series,d,thres=1e-5): 
    '''
    Constant width window (new solution)
    Note 1: thres determines the cut-off weight for the window
    Note 2: d can be any positive fractional, not necessarily bounded [0,1].
    '''
    #1) Compute weights for the longest series
    w=getWeights_FFD(d,thres,len(series))
    width=len(w)-1
    #2) Apply weights to values
    df={}
    for name in series.columns: 
        seriesF = series[[name]].fillna(method='ffill').dropna()
        df_=pd.Series([0]*len(seriesF)) 
        for iloc1 in range(width,seriesF.shape[0]):
            loc0,loc1=seriesF.index[iloc1-width],seriesF.index[iloc1]
            if not np.isfinite(series.loc[loc1,name]):continue # exclude NAs 
            df_.iloc[loc1]=np.dot(w.T,seriesF.loc[loc0:loc1])[0,0]
        df[name]=df_.copy(deep=True)
    df=pd.concat(df,axis=1)
    return df

def plotMinFFD(temp_series):
    from statsmodels.tsa.stattools import adfuller
    path,instName='/Users/jun/Documents/py/pairs_trading/record/','test'
    out=pd.DataFrame(columns=['adfStat','pVal','lags','nObs','95% conf','corr'])
    for d in np.linspace(0,1,11):
#         df1=np.log( pd.DataFrame( temp_series ) )
        df1=pd.DataFrame( temp_series )
        df1.columns = ['ClosePrice']
        df2=fracDiff_FFD(df1,d,thres=.01)
        corr=np.corrcoef(df1.loc[df2.index,'ClosePrice'],df2['ClosePrice'])[0,1]
        df3=adfuller(df2['ClosePrice'],maxlag=1,regression='c',autolag=None)
        out.loc[d]=list(df3[:4])+[df3[4]['5%']]+[corr] # with critical value
    out.to_csv(path+instName+'_testMinFFD.csv')
    out[['adfStat','corr']].plot(secondary_y='adfStat')
    plt.axhline(out['95% conf'].mean(),linewidth=1,color='r',linestyle='dotted')
    plt.savefig(path+instName+'_testMinFFD.png')
    return out

def check_stationary(column,temp):
    # 1 visual
    from pandas import Series
    from statsmodels.tsa.stattools import adfuller
    temp2 = temp[column][10:]
#     print(temp2[10:])
    plt.plot(range(len(temp2)),temp2,label= 'return (%)' )
    plt.plot()
    # 2 dicky fuller test
    series = temp2
    X = series.values
    result = adfuller(X,maxlag=None)
    print('ADF Statistic: %f' % result[0])
    print('p-value: %f' % result[1])
    print('Critical Values:')
    for key, value in result[4].items():
        print('\t%s: %.3f' % (key, value))
