# -*- coding: utf-8 -*-
"""

Trading strategies backtesting
Created by Juan Ignacio Gil Gomez, 2017-04-15

"""

import pandas as pd
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
        """Example of docstring on the __init__ method.

        Parameters
        ----------
        **kwargs
            quotes : Quote
                Quote instance, with market data.
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
        self.start_date = kwargs.get('start_date', pd.to_datetime('today') - pd.Timedelta(days=365))
        self.end_date = kwargs.get('end_date', pd.to_datetime('today'))
        self.quotes = kwargs.get('quotes', Quotes(start_date=self.start_date, end_date=self.end_date))
        self.open_signal = kwargs.get('open_signal', None)
        self.close_signal = kwargs.get('open_signal', None)

        # If quotes is not a Quotes instance, but a list of ticker symbols, generate a Quote from them
        if isinstance(self.quotes, list):
            if all([isinstance(q, str) for q in self.quotes]):
                self.quotes = Quotes(self.quotes, start_date=self.start_date, end_date=self.end_date)

    def __str__(self):
        s = '\n'.join(['Symbols: {}'.format(sorted(self.quotes.data.keys())),
                      'Start: {}'.format(self.start_date),
                      'End: {}'.format(self.end_date),
                      'Open Signal: {}'.format(self.open_signal),
                      'Close Signal: {}'.format(self.close_signal)])
        return s

# Main function

# Generates an instance of Quote and download the data from Google Finance for the default list of equities
if __name__ == "__main__":

    s = Strategy()
    print(s)