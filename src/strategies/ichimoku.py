#!/usr/bin/python3
import ta,requests,json,pandas
from ta.trend import IchimokuIndicator
from ta.utils import dropna
from matplotlib.patches import Rectangle

#Auxiliar function definitions
def compareLast(serieA, serieB, shiftBC=0, shiftA=0, serieC=''):
    if (serieA.iloc[shiftA if shiftA else -1] > serieB.iloc[shiftBC if shiftBC else -1]) & ((serieA.iloc[shiftA if shiftA else -1] > serieC.iloc[shiftBC if shiftBC else -1]) if type(serieC) != str else True): return 1
    if (serieA.iloc[shiftA if shiftA else -1] < serieB.iloc[shiftBC if shiftBC else -1]) & ((serieA.iloc[shiftA if shiftA else -1] < serieC.iloc[shiftBC if shiftBC else -1]) if type(serieC)!=str else True) : return -1
    return 0

#Ichimoku Functions
def ichimokuCalculate(reqdf):
    reqdf = dropna(reqdf)
    
    ichimokudf = pandas.DataFrame()
    ichimoku = IchimokuIndicator(high=reqdf['high'] ,low=reqdf['low'])

    ichimokudf['ichimoku_a'] = ichimoku.ichimoku_a()
    ichimokudf['ichimoku_b'] = ichimoku.ichimoku_b()
    ichimokudf['ichimoku_conversion_line'] = ichimoku.ichimoku_conversion_line()
    ichimokudf['ichimoku_base_line'] = ichimoku.ichimoku_base_line()
    ichimokudf['ichimoku_lagging_span'] = reqdf['close']
    ichimokudf['close'] = reqdf['close']
    ichimokudf['timestamp'] = reqdf['timestamp']
    
    ichimokudf.to_csv('../tmp/ichimoku.csv', encoding='utf-8')
    ichimokudf = pandas.read_csv('../tmp/ichimoku.csv', sep=',')

    return ichimokudf
    
def ichimokuAnalyze(ichimokudf,margin,trade = None):
    #Analyzing DataFrame

    #If there is an open trade then check if it is reverting
    if(trade):
        conditions = 0
        
        #Looking for revertion on conversion and baseline
        emastatus = compareLast(ichimokudf.ichimoku_conversion_line, ichimokudf.ichimoku_base_line)
        if trade['direction'] == 'long' and emastatus != 1: conditions += 2               
        if trade['direction'] == 'short' and emastatus != -1: conditions += 2

        
    #If there isn't any open trade then check for signals
    else:
        #Declaration
        conditions = 0
        #Conversion and baseline
        conditions += compareLast(ichimokudf.ichimoku_conversion_line, ichimokudf.ichimoku_base_line)
        #Cloud
        conditions += compareLast(ichimokudf.ichimoku_a, ichimokudf.ichimoku_b)
        #Price
        conditions += compareLast(ichimokudf.close, ichimokudf.ichimoku_a, serieC=ichimokudf.ichimoku_b, shiftBC=-26)
        #Lagging Span
        conditions += compareLast(ichimokudf.ichimoku_lagging_span, ichimokudf.ichimoku_a, serieC=ichimokudf.ichimoku_b, shiftBC=-26*2)

        #Decalaration 2
        conditions2 = 0
        #Conversion and baseline 2
        conditions2 += compareLast(ichimokudf.ichimoku_conversion_line, ichimokudf.ichimoku_base_line, shiftA=-margin, shiftBC=-margin)
        #Cloud 2
        conditions2 += compareLast(ichimokudf.ichimoku_a, ichimokudf.ichimoku_b, shiftA=-margin, shiftBC=-margin)
        #Price 2
        conditions2 += compareLast(ichimokudf.close, ichimokudf.ichimoku_a, serieC=ichimokudf.ichimoku_b, shiftBC=-26-margin, shiftA=-margin)
        #Lagging Span 2
        conditions2 += compareLast(ichimokudf.ichimoku_lagging_span, ichimokudf.ichimoku_a, serieC=ichimokudf.ichimoku_b, shiftBC=-(26*2)-margin, shiftA=-margin)

        #Analyzing conditions
        if (abs(conditions)== 4) and (conditions2 != conditions): 
            result = (True, conditions)
        else: 
            result = (False, conditions)
        
        #Calculating stoploss and takeprofit
        sl = 0
        tp = 0
        direction = ''
        #Long    
        if(result[0] and result[1] == 4): 
            sl = min(ichimokudf.ichimoku_a.iloc[-26],ichimokudf.ichimoku_b.iloc[-26]) - (ichimokudf.close.iloc[-1] * 0.01)
            tp = ichimokudf.close.iloc[-1] + ((ichimokudf.close.iloc[-1] - ichimokudf.ichimoku_b.iloc[-26]) * 2)
            direction = 'Long'
        #Short
        if(result[0] and result[1] == -4):
            sl = max(ichimokudf.ichimoku_a.iloc[-26],ichimokudf.ichimoku_b.iloc[-26]) + (ichimokudf.close.iloc[-1] * 0.01)
            tp = ichimokudf.close.iloc[-1] - ((ichimokudf.ichimoku_a.iloc[-26] - ichimokudf.close.iloc[-1]) * 2)
            direction = 'Short'
        #Returns
        if(sl and tp):
            return { 'direction': direction, 'stoploss': sl, 'takeprofit': tp, 'opentime':ichimokudf.timestamp.iloc[-1] }
        else:
            return None
                         
def ichimokuPlot(ichimokudf, plt, fig, ax, trade=None):
    
    if(trade != None):
        #TODO: CHANGE 100 to limit variable
        ax.add_patch(Rectangle((len(ichimokudf.close)-30, ichimokudf.close.iloc[-1]), 10,trade['takeprofit'] - ichimokudf.close.iloc[-1],
             facecolor = '#B8DEAB',
             fill=True,
             alpha=0.75,
             lw=5))
        #TODO: CHANGE 100 to limit variable
        ax.add_patch(Rectangle((len(ichimokudf.close)-30, trade['stoploss']), 10,ichimokudf.close.iloc[-1] - trade['stoploss'],
             facecolor = '#F5A5A5',
             alpha=0.75,
             fill=True,
             lw=5))
        ax.plot(ichimokudf.ichimoku_a, label='Ichimoku A', color='#53B96A', linewidth=0)
            
    ax.plot(ichimokudf.ichimoku_a, label='Ichimoku A', color='#53B96A', linewidth=0)
    ax.fill_between(ichimokudf.ichimoku_a.index, ichimokudf.ichimoku_a, ichimokudf.ichimoku_b, where=ichimokudf.ichimoku_a >= ichimokudf.ichimoku_b, facecolor='#53B96A', alpha=0.5, interpolate=True)
    ax.fill_between(ichimokudf.ichimoku_b.index, ichimokudf.ichimoku_a, ichimokudf.ichimoku_b, where=ichimokudf.ichimoku_a <= ichimokudf.ichimoku_b, facecolor='#E9838D', alpha=0.5, interpolate=True)
    ax.plot(ichimokudf.ichimoku_base_line.shift(periods=-26), label='Base Line', color='#FFC107', linewidth=1)
    ax.plot(ichimokudf.ichimoku_conversion_line.shift(periods=-26), label='Conversion Line', color='#007BFF', linewidth=1)
    ax.plot(ichimokudf.close.shift(periods=-26*2), label='Lagging Span', color='#7F00FF', linewidth=1)

    #TODO: Change BTCUSDT to symbol variable
    plt.savefig(f'../tmp/Ichimoku-BTCUSDT.png')
