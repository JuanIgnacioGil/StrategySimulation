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
                By default, mimic_open
            close_signal : function
                Function that returns a list with position changes at market close
                By default, close_daily_positions
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
        self.open_signal = kwargs.get('open_signal', mimic_open)
        self.close_signal = kwargs.get('open_signal', close_daily_positions)
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

    def backtest(self):
        """Backtest the strategy with the data stored in self.quotes

        Parameters
        ----------
        **kwargs
        
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

        dates = [t for t in pd.date_range(self.start_date, self.end_date) if t in self.quotes.close.index]

        open_actions = pd.DataFrame(index=dates, columns=self.quotes.symbols)
        close_actions = pd.DataFrame(index=dates, columns=self.quotes.symbols)

        for t in dates:
            open_actions.loc[t, :] = self.open_signal(t, self.quotes, open_actions, close_actions)
            close_actions.loc[t, :] = self.close_signal(t, self.quotes, open, close_actions)

        # Now we can calculate the pnl without loops
        pnl = -open_actions * self.quotes.open.loc[dates, :] -\
              close_actions * self.quotes.close.loc[dates, :] - \
              (abs(open_actions) + abs(close_actions)) * self.spread

        return pnl, open_actions, close_actions


# Strategies

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



# Main function

# Generates an instance of Quote and download the data from Google Finance for the default list of equities
if __name__ == "__main__":

    import matplotlib.pyplot as plt
    s = Strategy(start_date=pd.datetime(2016, 1, 1), end_date=pd.datetime(2017, 1, 1),
                 open_signal=mimic_open, close_signal=close_daily_positions)

    pnl, open_actions, close_actions = s.backtest()
    pnl.sum(axis=1).cumsum().plot()
    pnl.sum(axis=1).plot(kind='hist')
    plt.show()