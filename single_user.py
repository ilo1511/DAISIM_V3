from builtins import abs
import cvxpy as cp
import numpy as np
from numpy.ma import abs
from math import log as math_log
from math import exp
from util import *

# Assets are in individual units
x_base = np.array([100, 0, 0, 0])
assets = np.sum(x_base)

debug = False

def get_optimization_params():
    mu = np.array([.08, .22, .18, .16, 0.18])  # returns

    cor = np.array([[1, 0, 0, 0, 0], [0, 1, 0.2, 0.9, 0.2], [0, 0.2, 1, 0.1, 1], [0, 0.9, 0.1, 1, 0.1],
                    [0, 0.2, 1, 0.1, 1]])  # correlation matrix

    # Diag(std dev)
    d = np.array(
        [[0.2, 0, 0, 0, 0], [0, 0.8, 0, 0, 0], [0, 0, 0.3, 0, 0], [0, 0, 0, .5, 0],
         [0, 0, 0, 0, 0.3]])

    return mu, cor, d

## w = risk aversion!
def optimize(belief_factor, x_start, rho, txf, cdprate, w, h, eth_price, dai_price, eth_price_last_period, alpha_1, alpha_2, debug=True):
    # Compute asset worth given ETH Price
    asset_prices = np.array([1, eth_price, dai_price, eth_price])
    assets_dollars = np.multiply(x_start, asset_prices)
    money = np.sum(assets_dollars)

    # Initial dollar worth
    xo = cp.Parameter(4, nonneg=True)
    xo.value = assets_dollars

    mu, cor, d = get_optimization_params()

    # Covariance Matrix
    cvr = (d.dot(cor)).dot(d)

    x = cp.Variable(5)
    eth = x[1]
    dai1 = x[2]
    ceth = x[3]
    dai2 = x[4]

    # include cost of buying ceth as well
    # modified transaction fees
    tx_fee = cp.abs(x[1] - xo[1] + x[3] - xo[3]) * txf + cp.abs(x[2] - xo[2]) * txf

    # Calculate the price difference of ETH between this period and the last
    delta_eth_price = eth_price - eth_price_last_period

    # Herd behavior term: investor follows the trend to buy more if price is increasing, sell if decreasing
    herd_behavior = h * (exp (alpha_1 * delta_eth_price/eth_price_last_period) - exp(alpha_2 * ( - (delta_eth_price/eth_price_last_period))))  * eth

    # objective function updated with herd behavior
    objective = cp.Maximize(mu.T @ x - w * cp.quad_form(x, cvr) - cdprate * ceth - tx_fee + belief_factor*(dai2/dai_price)*(dai_price-1) - belief_factor*(dai1/dai_price)*(dai_price-1) + herd_behavior)
    
    # constraints remain the same
    constraints = [x[0] + x[1] + x[2] + x[3] == money, x >= 0, x[4] == x[3] / rho, x[0] >= tx_fee]

    prob = cp.Problem(objective, constraints)
    prob.solve(solver=cp.OSQP)

    if prob.status != "optimal":
        print("Not optimal!")
        x_temp = [i for i in x_start]
        return x_temp

    optimal_assets_in_dollars = [float(i) for i in x.value]
    transaction_fees = abs(
        optimal_assets_in_dollars[1] - xo.value[1] + optimal_assets_in_dollars[3] - xo.value[3]) * txf + abs(
        optimal_assets_in_dollars[2] - xo.value[2]) * txf

    optimal_assets_in_dollars[0] -= transaction_fees

    if debug:
        print("------------------- Iteration ----------------------------")
        print("CDP Rate: " + str(cdprate) + "\nRisk Averseness: " + str(w))
        print("TxFees: $%.2f" % transaction_fees)

    assets_dollars = optimal_assets_in_dollars[:-1]

    x_temp = np.divide(assets_dollars, asset_prices).clip(min=0)

    if debug:
        printAssets(x_temp, eth_price, dai_price, rho)
        print("--------------------- Ends -------------------------------")

    return x_temp


    if debug:
        printAssets(x_temp, eth_price, dai_price, rho)
        print("--------------------- Ends -------------------------------")

    return x_temp


# Pass asset distribution, ethereum price
def run_loop(eth_price):
    w = 0.001  # Risk Averseness
    rho = 2.5  # Liquidation Ratio

    h = [1, 2, 3]  # example herd behavior values for three investors
    for i, cdp_rate in enumerate([0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.34]):
        x = optimize(x_base, rho, 0.04, cdp_rate, w, eth_price, 1, eth_price, h[i % len(h)], False)


if __name__ == '__main__':
    run_loop(130)
