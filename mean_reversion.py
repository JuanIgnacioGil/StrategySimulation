import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from dateutil.relativedelta import relativedelta

def mean_reversion_open(t, quotes, open_actions, close_actions):
    """Mean reversion strategy at session open:
    
        Adjust a mean reversion model for all quotes using the last month of open data (both close and open)

        Buy 1 stock at market open of the 25% of stocks that are more underpriced according to the model 
        (only if the model predicts it will go up). 

        Short sell 1 stock at market open, of 25% of stocks that are more overpriced according to the model
        (only if the model predicts if will go down).

        Stay neutral for the other.

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

    Raises
    ----------
    ValueError
        If there is not enough data en self.quotes.close
    """

    month_ago = t - relativedelta(months=1)

    try:
        previous_month = quotes.close.index[(quotes.close.index >= month_ago) & (quotes.close.index < t) ]
    except:
        date_error = 'Cannot find data for the previous month to {} in self.quotes.close'.format(t)
        raise (ValueError(date_error))

    # Calibrate mean reversion model
    # (we are considering t in sessions, so dt for the weekend is still 1)
    data = quotes.open.loc[previous_month, :]
    z = np.log(data)
    dz = z - z.shift(1)
    zpred = []
    nd = z.shape[0] - 1

    for s in quotes.symbols:
        lm = LinearRegression(fit_intercept=True)
        y = dz.loc[dz.index[1:], s].as_matrix().reshape((nd, 1))
        x = z.loc[z.index[:-1], s].as_matrix().reshape((nd, 1))
        lm.fit(x, y)
        zpred.append(lm.predict(z.loc[z.index[-1], s]))

    # Calculate the percentiles
    barriers = np.percentile(zpred, [100 / 3, 2 * 100 / 3])
    buy_sell = []

    for s in zpred:
        if s <= min(barriers[0], 0):
            buy_sell.append(-1)
        elif s >= max(barriers[1], 0):
            buy_sell.append(1)
        else:
            buy_sell.append(0)

    return buy_sell


# Main function

if __name__ == "__main__":
    from strategies import Strategy, close_daily_positions
    import matplotlib.pyplot as plt

    # Generate an instance of Strategy with the default market data
    st = Strategy(start_date=pd.datetime(2016, 1, 1),
                  end_date=pd.datetime(2017, 1, 1),
                  open_signal=mean_reversion_open,
                  close_signal=close_daily_positions)

    # List of strategies to test


    # Backtest
    b = st.backtest(csv_file='mean_reversion.csv')
    print(b[0].sum().sum())
    b[0].sum(axis=1).cumsum().plot()
    plt.show()
