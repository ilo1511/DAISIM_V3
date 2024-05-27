!! README IS MOSTLY COPIED FROM SOURCE RESPOSITORY ANRGUSC/DAISIM

# DAISIM
The repository contains code for simulating a population of investors in the DAI Ecosystem. 

- `sim.py` is a CLI to run a single MAKER DAO market simulation using a test config as input.
- `simulation_util.py` contains MAKER DAO market simulation code.
- `single_user.py` contains CVXPY optimization code for an optimal investor.
- `test_runner.py` is a test runner to run a MAKER DAO market simulations using multiple test configs.
- `plot_gen.py` generates multiple plots from the simulation output i.e. `sim-summary.pickle`.
- `util.py` contains all utility functions.
- `input_generator.py` is a CLI to generate test configs for a factorial experiment.

- Install `cvxpy, pickle, numpy, scipy, matplotlib, tikzplotlib`
### Setup

### Market Simulations
- A single market simulation takes in some inputs,
    - `cdp_rate`: CDP Rate for creating a MAKER CDP.
    - `tx_fee`: Transaction fee for buying/selling of ETH/DAI/cETH.
    - `eth_price_feed`: ETH Price over several days. For a n-day market simulation this is vector of size `n` containing ETH price for each day. 
    - `dai_price`: Initial Price of DAI. Set to $1.
    - `num_investors`: Number of optimal investors participating in the market simulation.
    - `assets_and_risk`: Initial asset holdings, risk preference and herding factor for all investors. This is a vector of size `(num_investors,6)` with each 
    investors `assets_and_risk` a vector `[USD, ETH, DAI, cETH, risk_param]`.
            - A lower numerical value for risk translates to high risk.
            - A lower numerical value for herding translates to lower herding
    - `belief_factor`: A constant indicating the strength of investors' belief that the price of DAI is 1.
    - 'alpha': a constant that influences the price change sensitivity of our herding exponential function
   

- A sample config file is shown below for a MAKER DAO market simulation for a set of `tx_fee` and `cdp_rate` combinations. The config
will be used to run 5 * 3 = 15 single market simulations with the given asset allocations and risk parameters for 10 investors.
```editorconfig
6 7 0.01                                    // cdp_rate = [0.02, 0.03, 0.04, 0.05, 0.06]
1 2 0.01                                     // tx_fees = [0.05, 0.06, 0.07]
50 50 150 200                                // ETH Price  (4-day market simulation)
10                                           // num_investors
1840 5 1840 0 0.001 4                        // Investor#0 Assets, Risk = 0.001, Herding = 4
970 4 970 0 0.01 1                            // Investor#1 Assets, Risk = 0.001, Herding = 1
900 8 900 200 0.001 4                         // Investor#2 Assets, Risk = 0.01, Herding = 1
710 5 710 300 0.01 1                           // Investor#3 Assets, Risk = 0.01, Herding = 1
840 6 840 50 0.001 4                            // Investor #4 Assets, Risk = 0.001, Herding = 4
1040 2 1040 20 0.01 1                            // Investor #5 Assets, Risk = 0.01, Herding = 1
1360 8 1360 80 0.001 4                        // Investor #6 Assets, Risk = 0.001, Herding = 4
870 8 870 0 0.01 1                            // Investor #7 Assets, Risk = 0.01, Herding = 1
1340 7 1340 0 0.001 4                        // Investor #8 Assets, Risk = 0.001, Herding = 4
890 4 890 0 0.01 1                        // Investor #9 Assets, Risk = 0.01, Herding = 1
10                                            // belief_factor = 10
1                                            // alpha = 1
```

!!!! COMMANDS ARE IDENTIC TO BASE CODE, ONLY FIRST ONE WORKS CURRENTLY

- Running MAKER DAO market simulations,
    - `python3 sim.py --config path/to/config --logdir path/to/log/directory --days_per_config num_days_per_config` : Running this generates a file `sim-summary.pickle` inside the log directory
    which is used to generate useful plots.
    - `python3 plot_gen.py --data path/to/log/directory/sim-summary.pickle` : Running this generates several useful plots for the simulation. All generated plots would show up in a `plots`
    directory under the log directory.
    - `python3 test_runner.py --logdir /path/to/log/directory --configdir /path/to/config/directory` : Running this performs market simulation with several test configs under a single directory i.e configdir.
