# StrategySimulation #

A small Python library to download data from Google Finance and backtest trading strategies. It has been written and tested with Python 3.5 (using pandas 0.19.1 and numpy 1.11.2)

## Description ##

The class ```Quotes``` downloads and stores data from Google Finance. For example:

```python
quotes = Quotes(trading_universe=['AAPL', 'IBM'], 
				start_date='2017-1-1')
```

downloads from Google Finance data for Apple and IBM since the start of 2017 until today. If no equity symbols are given, data for a default set of equities is downloaded.

The class ```Strategies``` backtest trading strategies that can be executed at start and end of the day. Trading strategies can be easily implemented as functions in the form

```python
actions = buy_at_start(t, quotes, open_actions, close_actions)
```

Where ```t``` is the date, ```quotes``` is an instance of ```Quotes```, and ```open_actions``` and ```close_actions``` are arrays with the volumes buy or sold at the previous open and close.

For example:

```python
st = Strategy(
	quotestart_date=pd.datetime(2016, 1, 1), 
	end_date=pd.datetime(2017, 1, 1), 
	quotes=quotes, 
	open_signal=buy_at_start, 
	close_signal=do_nothing)

pnl, open_actions, close_actions = st.backtest()
```

Would backtest a buy and hold strategy with the quote generated before, and create a csv file with the daily pnl.


We also can backtest several strategies at once, with the function ```summary```:

```python
# Generate an instance of Strategy with the default market data
st = Strategy(start_date=pd.datetime(2016, 1, 1), 
end_date=pd.datetime(2017, 1, 1))

# List of strategies to test
strategies = [('mimic', mimic_open, close_daily_positions),
         ('volatility', volatility_strategy, close_daily_positions)]

# Backtest
st.summary(strategies, decimals=2)
```

would backtest two different strategies, *mimic* and *volatility*, and generate the csv files with the pnl and a text file called ```summary.txt``` with a summary of the results.

## Strategies implemented ##

We have implemented some example strategies in the file ```strategies.py```:

###buy\_at\_start ###
 Buy a stock of each asset if it's the first day of strategy. Stay neutral otherwise
###hold###
Do nothing
###close_all###
Close all open positions (this is executed at the end of every backtesting, to calculate the portfolio value)

###mimic_open###

Mimic strategy at session open:
    
* Buy 1 stock at market open, if the close price of the previous trading day was higher than the open price of the previous trading day. 
* Short sell 1 stock at market open, if the close price of the previous trading day
* Stay neutral otherwise.

###close\_daily\_positions###
* Close all positions opened at session open

###volatility_strategy###

* Buy 1 stock at market open, if daily volatility has reduced during the last trading day. That is, buy if
	
		(close - open) * (close - open) of the last trading day
		 < (close - open) * (close - open) of two trading days ago
                

* Short sell 1 stock at market open, if daily volatility has increased during the last trading day. That is, short sell if
                
 		(close - open) * (close - open) of the last trading day 
 		> (close - open) * (close - open) of two trading days ago.
 		
## Other libraries ##

This repository is just a small experiment. For any serious use, there are far better options, as:

* [Zipline](https://github.com/quantopian/zipline)
* [backtrader](https://github.com/mementum/backtrader)
 		
 


