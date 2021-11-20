#!/usr/bin/python3
#Imports
import ta,requests,json,pandas
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.patches import Rectangle
#Test imports
from strategies.ichimoku import ichimokuCalculate, ichimokuAnalyze, ichimokuPlot

def getData(interval,symbol,limit,firstcandles=0):
    rawCandles=json.loads(requests.get(f'https://api1.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}').content.decode())

    firstcandles = firstcandles if firstcandles else len(rawCandles[0])
    
    ts = [candle[0] for candle in rawCandles][:firstcandles]
    op = [candle[1] for candle in rawCandles][:firstcandles]
    high = [candle[2] for candle in rawCandles][:firstcandles]
    low = [candle[3] for candle in rawCandles][:firstcandles]
    close = [candle[4] for candle in rawCandles][:firstcandles]
    vol = [candle[5] for candle in rawCandles][:firstcandles]

    formatedCandles = {'timestamp': ts, 'open': op, 'high': high, 'low': low, 'close': close, 'volume': vol}

    reqdf = pandas.DataFrame(formatedCandles)
    
    reqdf.to_csv('../tmp/request.csv', encoding='utf-8')
    reqdf = pandas.read_csv('../tmp/request.csv', sep=',')

    return reqdf
    




def plotDefaults(reqdf, title):
    mpl.style.use('seaborn')

    fig, ax = plt.subplots()

    plt.title(title)
    
    #widths of candlestick
    width = .4
    width2 = .05
    #up and down prices

    up = reqdf.loc[reqdf.close > reqdf.open]
    down =  reqdf.loc[reqdf.close < reqdf.open]
    #colors in candlestick
    col1 = 'green'
    col2 = 'red'

    #plot up prices
    ax.bar(up.index- 26,up.close-up.open,width,bottom=up.open,color=col1)
    ax.bar(up.index- 26,up.high-up.close,width2,bottom=up.close,color=col1)
    ax.bar(up.index- 26,up.low-up.open,width2,bottom=up.open,color=col1)
    
    #plot down prices
    ax.bar(down.index- 26,down.close-down.open,width,bottom=down.open,color=col2)
    ax.bar(down.index- 26,down.high-down.open,width2,bottom=down.open,color=col2)
    ax.bar(down.index- 26,down.low-down.close,width2,bottom=down.close,color=col2)

    return (plt,fig,ax)

def main():
    if __name__ == '__main__':
        #Params
        interval='1h'
        symbol = 'BTCUSDT'
        limit='100'
        firstcandles = 100
        strategy_name = "ichimoku"
        reqdf = getData(interval, symbol, limit, firstcandles)

        plt, fig, ax = plotDefaults(reqdf, f'{symbol} {interval}')
        strategydf = eval(f"{strategy_name}Calculate(reqdf)")
        eval(f"{strategy_name}Plot(strategydf, plt, fig, ax, {strategy_name}Analyze(strategydf, 1))")
        #ichimokudf = ichimokuCalculate(reqdf)
        #ichimokuPlot(ichimokudf, plt, fig, ax, ichimokuAnalyze(ichimokudf, 1) )
        
        #Show the graphic
        plt.legend()
        plt.show()
main()