# -*- coding: utf-8 -*-
"""Example NumPy style docstrings.

Download quotes from Google Finance

"""

import pandas as pd
import pandas_datareader.data as web
from warnings import warn

default_trading_universe = ['AAPL', 'noexiste', 'AXP', 'BA', 'CAT', 'CVX', 'CSCO', 'DIS', 'DD', 'XOM', 'GE', 'GS', 'HD', 'IBM',
                    'INTC', 'JNJ', 'JPM', 'KO', 'MCD', 'MMM', 'MRK', 'MSFT', 'NKE', 'PFE', 'PG', 'TRV', 'UTX',
                    'UNH', 'VZ', 'V', 'WMT']

"""default_trading_universe : list of str

Default trading universe
"""

def download_quote(ticker, start_date=pd.to_datetime('today') - pd.Timedelta(days=365),
                   end_date=pd.to_datetime('today')):
    """
    Downloads historical data of a quote from Google Finance

    Parameters
    ----------
    ticker : str
        Ticker symbol
    start_date : date
        First historical date to retrieve
        Defaults to 1 year ago
    end_date : date
        Last historical date to retrieve.
        Defaults to today

    Returns
    -------
    bool
        True if successful, False otherwise.
    """

    quote = web.DataReader(ticker, 'google', start_date, end_date)

    return quote


class Quotes():
    """Class to download and store quotes

    Attributes
    ----------
    data : dict
        Dictionary in the form {'symbol': pd.DataFrame}, where every DataFrame has columns
        ['Open', 'High', 'Low', 'Close', 'Volume'] and date as index
    """

    def __init__(self, trading_universe=default_trading_universe):

        # If we work with a single quote, convert it to a list
        if isinstance(trading_universe, str):
            trading_universe = [trading_universe]

        self.data = {q: pd.DataFrame(columns=['Open', 'High', 'Low', 'Close', 'Volume'])
                     for q in trading_universe}

    def __str__(self):

        s = ''
        separator = ''.join(50 * ['-'])

        for q, df in self.data.items():
            s += '{}:\n{}\n{}\n'.format(q, df.describe(), separator)

        return s

    def download(self, start_date=pd.to_datetime('today') - pd.Timedelta(days=365), end_date=pd.to_datetime('today')):
        """Downloads historical data from Google Finance for all quotes in the trading universe of the object

        Parameters
        ----------
        start_date : date
            First historical date to retrieve
            Defaults to 1 year ago
        end_date : date
            Last historical date to retrieve.
            Defaults to today

        Warnings
        ----------
        
        """

        for ticker in self.data.keys():
            try:
                self.data[ticker] = download_quote(ticker, start_date, end_date)
            except:
                w_string = 'No data for {}'.format(ticker)
                warn(w_string)



# Main function

# Generates an instance of Quote and download the data from Google Finance for the default list of equities
if __name__ == "__main__":

    quotes = Quotes()
    quotes.download(start_date=pd.datetime(2016, 1, 1), end_date=pd.datetime(2017, 1, 1))
    print(quotes)