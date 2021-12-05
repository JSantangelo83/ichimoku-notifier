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
    ichimokudf['high'] = reqdf['high']
    ichimokudf['low'] = reqdf['low']
    ichimokudf['timestamp'] = reqdf['timestamp']
    
    ichimokudf.to_csv('../tmp/ichimoku.csv', encoding='utf-8')
    ichimokudf = pandas.read_csv('../tmp/ichimoku.csv', sep=',')

    return ichimokudf
    
def ichimokuAnalyze(ichimokudf,margin,trade = None):
    #Analyzing DataFrame

    #If there is an open trade then check if it is reverting
    if(trade):
        #Check dynamic stop loss
        #TODO: Improve hardcoded SL Levels
        #TODO: Improve short|long hardcoded math
        
        if (trade['direction'] == 'long') and (ichimokudf.close.iloc[-1] > trade['openprice']):
                #Difference Achieved TP
                datp = ichimokudf.high.iloc[-1] - trade['openprice']
                #Difference TP
                dtp = trade['takeprofit'] - trade['openprice']

                #Percentaje Achieved TP
                patp = dtp / datp
                                
                #25% Takeprofit --> SL = 0.1%
                if (patp <= 4) and (trade['stoploss'] < trade['openprice']):
                    trade['stoploss'] = trade['openprice'] + (trade['openprice'] * 0.003)
                    return [3, trade]                
                #50% Takeprofit --> SL = 25%
                if (patp <= 2) and (trade['stoploss'] < (trade['takeprofit'] - ((dtp / 4) * 3))):
                    trade['stoploss'] = trade['takeprofit'] - ((dtp / 4) * 3)
                    return [3, trade]
                #75% Takeprofit --> SL = 50%
                if(patp <= 1.3) and (trade['stoploss'] < (trade['takeprofit'] - (dtp / 2))): 
                    trade['stoploss'] = trade['takeprofit'] - (dtp / 2)
                    return [3, trade]
                    
        if (trade['direction'] == 'short') and (ichimokudf.close.iloc[-1] < trade['openprice']):
                #Difference Achieved TP
                datp = trade['openprice'] - ichimokudf.low.iloc[-1]
                #Difference TP
                dtp = trade['openprice'] - trade['takeprofit']

                #Percentaje Achieved TP
                patp = dtp / datp

                #25% Takeprofit --> SL = 0.1%
                if (patp <= 4) and (trade['stoploss'] > trade['openprice']):
                    trade['stoploss'] = trade['openprice'] - (trade['openprice'] * 0.003)
                    return [3, trade]                
                #50% Takeprofit --> SL = 25%
                if(patp <= 2) and (trade['stoploss'] > (trade['takeprofit'] + ((dtp / 4) * 3))):
                    trade['stoploss'] = trade['takeprofit'] + ((dtp / 4) * 3)
                    return [3, trade]
                #75% Takeprofit --> SL = 50%
                if(patp <= 1.3) and (trade['stoploss'] > (trade['takeprofit'] + (dtp / 2))): 
                    trade['stoploss'] = trade['takeprofit'] + (dtp / 2)
                    return [3, trade]

                    
        conditions = 0
        #Looking for revertion on conversion and baseline
        emastatus = compareLast(ichimokudf.ichimoku_conversion_line, ichimokudf.ichimoku_base_line) + compareLast(ichimokudf.ichimoku_conversion_line, ichimokudf.ichimoku_base_line, shiftA=-1, shiftBC=-1) + compareLast(ichimokudf.ichimoku_conversion_line, ichimokudf.ichimoku_base_line, shiftA=-2, shiftBC=-2)
        if trade['direction'] == 'long' and emastatus == -3: conditions += 2               
        if trade['direction'] == 'short' and emastatus == 3: conditions += 2
        #Looking for revertion by being in loss
        if trade['direction'] == 'long' and ichimokudf.close.iloc[-1] < trade['openprice']: conditions+=1
        if trade['direction'] == 'short' and ichimokudf.close.iloc[-1] > trade['openprice']: conditions+=1

        return [2, conditions]
        
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
            tp = ichimokudf.close.iloc[-1] + ((ichimokudf.close.iloc[-1] - (sl + ichimokudf.close.iloc[-1] * 0.01)) * 2)
            direction = 'long'
        #Short
        if(result[0] and result[1] == -4):
            sl = max(ichimokudf.ichimoku_a.iloc[-26],ichimokudf.ichimoku_b.iloc[-26]) + (ichimokudf.close.iloc[-1] * 0.01)
            tp = ichimokudf.close.iloc[-1] - ((sl - (ichimokudf.close.iloc[-1] * 0.01) - ichimokudf.close.iloc[-1]) * 2)
            direction = 'short'

        #Returns
        if(sl and tp):
            #TODO: Improve "plotcandle" property use
            return [1, { 
                        'direction': direction, 
                        'stoploss': sl, 
                        'takeprofit': tp, 
                        'openprice':ichimokudf.close.iloc[-1], 
                        'plotcandle':len(ichimokudf.close) 
                        }]
        else:
            return [0, None]
                         
def ichimokuPlot(ichimokudf, plt, fig, ax, trade=None):
    if(trade != None):
        # TODO: Fix SL and TP position
        ax.add_patch(Rectangle((trade['plotcandle'], trade['openprice']), 50, trade['takeprofit'] - trade['openprice'],
            facecolor='#B8DEAB',
            fill=True,
            alpha=0.75,
            lw=5))
        ax.add_patch(Rectangle((trade['plotcandle'], trade['stoploss']), 50, trade['openprice'] - trade['stoploss'],
            facecolor='#F5A5A5' if ((trade['direction'] == 'long') and (trade['stoploss'] < trade['openprice'])) or (trade['direction'] == 'short' and (trade['stoploss'] > trade['openprice'])) else '#2F7842',
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
