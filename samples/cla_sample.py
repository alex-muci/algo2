from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
import os
import matplotlib.pyplot as plt
import numpy as np

import algo2.utilities as utilities
from algo2.statistics.CLA import CLA


def plot2D(x,y,xLabel='',yLabel='',title='',pathChart=None):
    import matplotlib.pyplot as mpl
    fig = mpl.figure()
    ax = fig.add_subplot(1, 1, 1)  # one row, one column, first plot
    ax.plot(x, y, color='blue')
    ax.set_xlabel(xLabel)
    ax.set_ylabel(yLabel, rotation=90)
    mpl.xticks(rotation='vertical')
    mpl.title(title)
    if pathChart is None:
        mpl.show()
    else:
        mpl.savefig(pathChart)
    mpl.clf()   # reset pylab
    return


def run(config, testing, tickers_filename):

    # get path and load tickers data (in a single file)
    csv_dir = config.CSV_DATA_DIR
    path = os.path.join(csv_dir, tickers_filename)
    # headers = open(path, 'r').readline().split(',')[:-1]
    data = np.genfromtxt(path, delimiter=',', skip_header=1)  # load as numpy array  # ...,  names=True)

    mean = np.array(data[:1]).T  # get 2nd line (1st line, headers, skipped), then transpose -> mean
    l_b = np.array(data[1:2]).T  # get 3rd line ... -> lower bounds
    u_b = np.array(data[2:3]).T  # get 4th line ... -> upper bounds
    covar = np.array(data[3:])   # get 5th line and successive -> cov matrix

    # Call object and solve
    cla = CLA(mean, covar, l_b, u_b)
    cla.solve()
    # print(cla.w)  # print all turning points

    # get efficient frontier: [un-comment second line below for results]
    mu, sigma, weights = cla.eff_frontier(100)
    # print(weights)

    # 5) Get Maximum Sharpe ratio portfolio
    sr, w_sr = cla.get_max_sharpe()
    # print(np.dot(np.dot(w_sr.T, cla.covar), w_sr)[0, 0]**.5, sr)
    print("sr is: ", sr)
    print("w_sr are: ", w_sr)

    # 6) Get Minimum Variance portfolio
    mv, w_mv = cla.get_min_var()
    print("mv is: ", mv)
    print("w_mv are: ", w_mv)

    # plot if not in testing
    if testing is False:

        # plot efficient frontier
        plot2D(sigma, mu, 'Risk', 'Expected Excess Return', 'CLA-derived Efficient Frontier')

        # two sub-plots
        plt.figure()
        plt.subplot(211)
        plt.bar(np.arange(len(w_sr)), w_sr)
        plt.title('Maximum Sharpe ratio portfolio weights')
        plt.subplot(212)
        plt.bar(np.arange(len(weights[-1])), weights[-1])
        plt.title('Maximum risk portfolio weights')
        plt.show()

    else:   # get all main results in a dict for test file
        test_rslts = {
            "mu": mu, "sigma": sigma,
            "sharpe_ratio": sr, "min_sr_weight": min(w_sr), "max_sr_weight": max(w_sr),
            "mv": mv, "min_mv_weight": min(w_mv), "max_mv_weight": max(w_mv)
        }
        return test_rslts


##############################################
def main():
    config = utilities.DEFAULT
    testing = False
    tickers_filename = 'CLA_Data.csv'
    run(config, testing, tickers_filename)


##############################################
if __name__ == "__main__":
    main()
