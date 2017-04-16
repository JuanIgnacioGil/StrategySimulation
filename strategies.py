# -*- coding: utf-8 -*-
"""

Trading strategies backtesting
Created by Juan Ignacio Gil Gomez, 2017-04-15

"""

import pandas as pd
import numpy as np

from quotes import Quotes


class Strategy(object):
    """Class for strategy backtesting

    Attributes
    ----------
    quotes : Quotes
        instance of quotes, containing market data
    open_signal : function
        Function that returns a 'Buy', 'Close' or 'Neutral' signal at market open
    close_signal : function
        Function that returns a 'Buy', 'Close' or 'Neutral' signal at market close
    start_date : date
        First historical date to retrieve
        Defaults to 1 year ago
    end_date : date
        Last historical date to retrieve.
        Defaults to today
    """

    def __init__(self, **kwargs):
        """ __init__ method.

        Parameters
        ----------
        **kwargs
            quotes : Quote
                Quote instance, with market data.
            open_signal : function
                Function that returns a list with position changes at market open
                By default, buy_at_start
            close_signal : function
                Function that returns a list with position changes at market close
                By default, hold
            start_date : date
                First historical date to retrieve
                Defaults to 1 year ago
            end_date : date
                Last historical date to retrieve.
                Defaults to today
            spread : constant value to simulate bid/ask spread and fees
                Defaults to 0
        """
        self.start_date = kwargs.get('start_date', pd.to_datetime('today') - pd.Timedelta(days=365))
        self.end_date = kwargs.get('end_date', pd.to_datetime('today'))
        self.quotes = kwargs.get('quotes',
                                 Quotes(start_date=self.start_date - pd.Timedelta(days=30), end_date=self.end_date))
        self.open_signal = kwargs.get('open_signal', buy_at_start)
        self.close_signal = kwargs.get('close_signal', hold)
        self.spread = kwargs.get('spread', 0)

        # If quotes is not a Quotes instance, but a list of ticker symbols, generate a Quote from them
        if isinstance(self.quotes, list):
            if all([isinstance(q, str) for q in self.quotes]):
                self.quotes = Quotes(self.quotes, start_date=self.start_date, end_date=self.end_date)

    def __str__(self):
        s = '\n'.join(['Symbols: {}'.format(sorted(self.quotes.symbols)),
                      'Start: {}'.format(self.start_date),
                      'End: {}'.format(self.end_date),
                      'Open Signal: {}'.format(self.open_signal),
                      'Close Signal: {}'.format(self.close_signal)])
        return s

    def backtest(self, **kwargs):
        """Backtest the strategy with the data stored in self.quotes

        Parameters
        ----------
        **kwargs
            csv_file : str
                Path of the csv file to save the pnl DataFrame
                Defaults to '', and no file is written 
                
            open_signal : function
                open signal function. Defaults to self.open_signal
            
            close_signal : function
                close signal function. Defaults to self.open_signal
            
            decimals : int
                Number of decimals to get in the pnl (to make the result more readable. 
                Defaults to None, where no rounding is made)
                
             
        Returns
        ----------
        open_actions : pandas.DataFrame
            DataFrame with actions taken at session open (one column per symbol, where, for example, -1 represents
            selling 1 stock)
        close_actions : pandas.DataFrame
            DataFrame with actions taken at session open (one column per symbol, where, for example, 2 represents
            buying 2 stocks)
        pnl : pandas.DataFrame
            DataFrame with money win or lost each day for each symbol
        """

        csv_file = kwargs.get('csv_file', '')
        open_signal = kwargs.get('open_signal', self.open_signal)
        close_signal = kwargs.get('close_signal', self.close_signal)
        decimals = kwargs.get('decimals', None)

        dates = [t for t in pd.date_range(self.start_date, self.end_date) if t in self.quotes.close.index]

        open_actions = pd.DataFrame(0, index=dates, columns=self.quotes.symbols)
        close_actions = pd.DataFrame(0, index=dates, columns=self.quotes.symbols)

        for t in dates:
            open_actions.loc[t, :] = open_signal(t, self.quotes, open_actions, close_actions)

            # At last day closing we close all open position, regardless of the close signal
            if t == dates[-1]:
                close_actions.loc[t, :] = close_all(t, self.quotes, open_actions, close_actions)
            else:
                close_actions.loc[t, :] = close_signal(t, self.quotes, open_actions, close_actions)

        # Now we can calculate the pnl without loops
        pnl = -open_actions * self.quotes.open.loc[dates, :] -\
              close_actions * self.quotes.close.loc[dates, :] - \
              (abs(open_actions) + abs(close_actions)) * self.spread

        if decimals:
            pnl = pnl.round(decimals)

        # If asked, save the pnl in a csv file
        if csv_file:
            pnl.to_csv(csv_file)

        return pnl, open_actions, close_actions


# Strategies

def buy_at_start(t, quotes, open_actions, close_actions):
    """Buy a stock of each asset if it's the first day of strategy
        Stay neutral otherwise

    Parameters
    ----------
    t : date
        Date of the session

    quotes : Quotes
        Market data

    open_actions : pandas.DataFrame
        DataFrame with the actions taken in the session open

    close_actions : pandas.DataFrame
        DataFrame with the actions taken in the session close

    Returns
    ----------
    pandas.DataFrame
        DataFrame with the actions on the open of t
    """

    if t == open_actions.index[0]:
        actions = np.ones(open_actions.shape[1])
    else:
        actions = np.zeros(open_actions.shape[1])

    return actions


def hold(t, quotes, open_actions, close_actions):
    """Do nothing

    Parameters
    ----------
    t : date
        Date of the session

    quotes : Quotes
        Market data

    open_actions : pandas.DataFrame
        DataFrame with the actions taken in the session open

    close_actions : pandas.DataFrame
        DataFrame with the actions taken in the session close

    Returns
    ----------
    pandas.DataFrame
        DataFrame with the actions on the open of t
    """

    return np.zeros(open_actions.shape[1])


def close_all(t, quotes, open_actions, close_actions):
    """Close all open positions

    Parameters
    ----------
    t : date
        Date of the session

    quotes : Quotes
        Market data

    open_actions : pandas.DataFrame
        DataFrame with the actions taken in the session open

    close_actions : pandas.DataFrame
        DataFrame with the actions taken in the session close

    Returns
    ----------
    pandas.DataFrame
        DataFrame with the actions on the open of t
    """

    # Note that this assumes that actions start filled with zeros
    open_positions = (open_actions.loc[open_actions.index <= t,:] +
                      close_actions.loc[close_actions.index <= t,:]).sum().as_matrix()

    return -open_positions


def mimic_open(t, quotes, open_actions, close_actions):
    """Mimic strategy at session open:
    
        Buy 1 stock at market open, if the close price of the previous trading day was
        higher than the open price of the previous trading day. 
        
        Short sell 1 stock at market open, if the close price of the previous trading day
        was lower than the open price of the previous trading day. 
        
        Stay neutral otherwise.

    Parameters
    ----------
    t : date
        Date of the session
    
    quotes : Quotes
        Market data
        
    open_actions : pandas.DataFrame
        DataFrame with the actions taken in the session open
        
    close_actions : pandas.DataFrame
        DataFrame with the actions taken in the session close

    Returns
    ----------
    pandas.DataFrame
        DataFrame with the actions on the open of t
    """

    previous_day = max(quotes.close.index[quotes.close.index < t])
    previous_open = quotes.open.loc[previous_day, :]
    previous_close = quotes.close.loc[previous_day, :]

    return np.sign(previous_close - previous_open)


def close_daily_positions(t, quotes, open_actions, close_actions):
    """Close all positions opened at session open

    Parameters
    ----------
    t : date
        Date of the session

    quotes : Quotes
        Market data

    open_actions : pandas.DataFrame
        DataFrame with the actions taken in the session open

    close_actions : pandas.DataFrame
        DataFrame with the actions taken in the session close

    Returns
    ----------
    pandas.DataFrame
        DataFrame with the actions necessary to close all positions
    """

    return -open_actions.loc[t, :]


def volatility_strategy(t, quotes, open_actions, close_actions):
    """Volatility strategy

            Buy 1 stock at market open, if daily volatility has reduced during the last trading
            day. That is, buy if
                (close - open) * (close - open) of the last trading day <
                < (close - open) * (close - open) of two trading days ago.

            Short sell 1 stock at market open, if daily volatility has increased during the last
            trading day. That is, short sell if
                (close - open) * (close - open) of the last trading day >
                > (close - open) * (close - open) of two trading days ago.

    Parameters
    ----------
    t : date
        Date of the session

    quotes : Quotes
        Market data

    open_actions : pandas.DataFrame
        DataFrame with the actions taken in the session open

    close_actions : pandas.DataFrame
        DataFrame with the actions taken in the session close

    Returns
    ----------
    pandas.DataFrame
        DataFrame with the actions on the open of t
    """

    previous_day = max(quotes.close.index[quotes.close.index < t])
    two_days_ago = max(quotes.close.index[quotes.close.index < previous_day])

    vol_previous = (quotes.close.loc[previous_day, :] - quotes.open.loc[previous_day, :]) ** 2
    vol_two_days_ago = (quotes.close.loc[two_days_ago, :] - quotes.open.loc[two_days_ago, :]) ** 2

    return np.sign(vol_two_days_ago - vol_previous)


# Main function

# Generates an instance of Quote and download the data from Google Finance for the default list of equities
if __name__ == "__main__":
    from plotly import tools
    import plotly.offline as plotly
    import plotly.graph_objs as go

    s = Strategy(start_date=pd.datetime(2016, 1, 1), end_date=pd.datetime(2017, 1, 1),
                 open_signal=volatility_strategy, close_signal=close_daily_positions)

    pnl, open_actions, close_actions = s.backtest(csv_file='volatility.csv', decimals=2)

    trace1 = go.Scatter(x=pnl.index, y=pnl.sum(axis=1).cumsum())
    trace2 = go.Histogram(x=pnl.sum(axis=1))
    fig = tools.make_subplots(rows=2, cols=1)

    fig.append_trace(trace1, 1, 1)
    fig.append_trace(trace2, 2, 1)
    plotly.plot(fig)