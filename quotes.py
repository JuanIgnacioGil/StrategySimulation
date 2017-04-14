# -*- coding: utf-8 -*-
"""Example NumPy style docstrings.

Download quotes from Google Finance

"""

import pandas as pd

default_trading_universe = ['AAPL', 'AXP', 'BA', 'CAT', 'CVX', 'CSCO', 'DIS', 'DD', 'XOM', 'GE', 'GS', 'HD', 'IBM',
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

    # Generate the Google url
    url = ''.join(['http://www.google.com/finance/historical?q=NASDAQ%3A{}'.format(ticker),
                   '&startdate={}+{}+{}'.format(start_date.month, start_date.day, start_date.year),
                   '&enddate={}+{}+{}&output=csv'.format(end_date.day, end_date.month, end_date.year)])

    url = 'http://www.google.com/finance/historical?q=NASDAQ%3A{}&output=csv'.format(ticker)

    print(url)

    quote = pd.read_csv(url, index_col='Date')

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

        Returns
        -------
        bool
            True if successful, False otherwise.
        """

        for q in self.data.keys():
            self.data['q'] = download_quote(q, start_date, end_date)


# Main function

# Generates an instance of Quote and download the data from Google Finance for the default list of equities
if __name__ == "__main__":

    #quotes = Quotes()
    #quotes.download(start_date=pd.datetime(2016, 1, 1), end_date=pd.datetime(2017, 1, 1))
    q = download_quote('AAPL')
    print(q)