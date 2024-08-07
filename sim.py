from simulation_util import *
import multiprocessing as mp
import pickle
import os
import argparse

ASSETS = None
RISK = None
HERD = None


def run_on_thread(sample_size, belief_factor, assets, risk_params, herd_params, cdp_rate, tx_fee, run_index, eth_price_per_day, days_per_config, alpha_1, alpha_2,
                  logdir, logger): 
    dai_price_history = []
    market_dai_history = []

    assert (len(eth_price_per_day) >= days_per_config)

    asset_history = [assets[:]]
    cur_assets = assets
    cur_dai_price = 1
    for day in range(0, days_per_config):
        s = Simulator(belief_factor=belief_factor, rho=2.5, cdpRate=cdp_rate, txf=tx_fee, run_index=run_index, eth_price=eth_price_per_day[day],
                      sample_size=sample_size,
                      initial_distribution=cur_assets, risk_params=risk_params, herd_params=herd_params, alpha_1 = alpha_1, alpha_2 = alpha_2, logdir=logdir, logger=logger, eth_price_last_period=eth_price_per_day[day-1])
        s.dai_price = cur_dai_price
        dai_price, market_dai = s.run_simulation()

        # get asset state
        cur_assets = s.final_distribution
        cur_dai_price = dai_price

        # store asset_history and dump into a separate pickle file
        asset_history.append(cur_assets[:])

        dai_price_history.append(dai_price)
        market_dai_history.append(market_dai)

    return dai_price_history, asset_history



def generate_assets_and_params(sample_size, test_type, runs):
    # if ASSETS was populated from config, return. Else generate a random ASSETS
    if ASSETS is not None:
        return ASSETS, RISK, HERD, ALPHA_1, ALPHA_2

    assets_runs = [get_assets(sample_size, test_type) for k in range(runs)]
    risk_params, herd_params = get_risk_and_herd_params(sample_size)
    alpha_1, alpha_2 = get_alphas(sample_size)

    return assets_runs, risk_params, herd_params, alpha_1, alpha_2


def run_tests(sample_size, belief_factor, cdp_rates, tx_fees, runs, eth_price_per_day, days_per_config, test_type, logdir, logger,
              sumfile):
    # Get number of CPUs
    cpus = mp.cpu_count()
    pool_count = cpus * 2

    # Process pool to handle k simulations/process!
    pool = mp.Pool(processes=pool_count)

    args = []

    # Define initial allocation and risk distribution
    # If multiple runs, then each run has a different asset allocation, but same risk distribution.
    assets_runs, risk_params, herd_params, alpha_1, alpha_2 = generate_assets_and_params(sample_size, test_type, runs)

    for tx_fee in tx_fees:
        for cdp_rate in cdp_rates:
            for run in range(runs):
                args.append(
                    (sample_size, belief_factor, assets_runs[run], risk_params, herd_params, cdp_rate, tx_fee, run, eth_price_per_day,
                     days_per_config, alpha_1, alpha_2, logdir, logger)) 

    results = pool.starmap(run_on_thread, args)

    # Get all required parameters and dump to pickle
    belief_factor_axis = [args[i][1] for i in range(len(args))]
    risk_params_axis = [args[i][3] for i in range(len(args))]
    herd_params_axis = [args[i][4] for i in range(len(args))]
    cdp_axis = [args[i][5] for i in range(len(args))]
    txf_axis = [args[i][6] for i in range(len(args))]
    run_axis = [args[i][7] for i in range(len(args))]
    eth_price_per_day_axis = [args[i][8] for i in range(len(args))]
    alpha_1_axis = [args[i][10] for i in range(len(args))]
    alpha_2_axis = [args[i][11] for i in range(len(args))]


    dai_axis = [res[0] for res in results]
    asset_history = [res[1] for res in results]

    dump = [cdp_axis, txf_axis, run_axis, dai_axis, asset_history, risk_params_axis, herd_params_axis, belief_factor_axis, eth_price_per_day_axis, alpha_1_axis, alpha_2_axis]
    ##print(dai_axis)
    ##print("DUMP")
    pickle.dump(dump, sumfile)
    print(sumfile)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='MAKER Simulation CLI')

    parser.add_argument(
        "--investors",
        type=int,
        default=10,
        help="Number of participating investors in the simulation"
    )

    parser.add_argument(
        "--runs",
        type=int,
        default=1,
        help="Number of runs for each config pair"
    )

    parser.add_argument(
        "--type",
        type=str,
        default="normal",
        help="Can be either normal/uniform/random"
    )

    parser.add_argument(
        "--days_per_config",
        type=int,
        default=15,
        help="Number of days to run the simulation for each CDPRate TXF Pair"
    )

    parser.add_argument(
        "--log",
        type=bool,
        default=True,
        help="Logs simulation results in specified directory"
    )

    parser.add_argument(
        "--logdir",
        type=str,
        default="sim-logs",
        help="Log Directory. Creates if not found."
    )

    parser.add_argument(
        "--config",
        type=str,
        default="",
        help="Config File for test",
        required=True
    )
    

    args = parser.parse_args()
    # Clear log directory if found
    if os.path.exists(args.logdir):
        os.system("rm -rvf " + args.logdir + "/*")
    else:
        os.mkdir(args.logdir)

    summary_filename = "sim-summary.pickle"
    sumfile = open(os.path.join(args.logdir, summary_filename), "wb")

    # read  CDPRates, TXFs from config
    config = open(args.config, "r")
    config_lines = config.readlines()

    assert (len(config_lines) >= 3)

    cdp_config = config_lines[0].split(' ')
    txf_config = config_lines[1].split(' ')

    eth_price_per_day = list(map(float, config_lines[2].split(' ')))

    # If this happens, then assets/risk have been provided in the config
    assets = []
    risk_params = []
    herd_params = []
    alpha_1 = []
    alpha_2 = []
    if len(config_lines) > 3:
        # Config overrides parameters set in CLI, currently this only supports 1 run.
        print("Config might override parameters set by CLI")

        args.investors = int(config_lines[3])
        args.runs = 1
        for i in range(4, 4 + args.investors):
            line_split = list(map(float, config_lines[i].split(' ')))
            assert (len(line_split) == 8)

            assets.append(line_split[:-4])
            risk_params.append(line_split[-4])
            herd_params.append(line_split[-3])
            alpha_1.append(line_split[-2])
            alpha_2.append(line_split[-1])

        # Fix global values of ASSETS, RISK
        ASSETS = [assets]
        RISK = risk_params
        HERD = herd_params
        ALPHA_1 = alpha_1
        ALPHA_2 = alpha_2
        
    if len(eth_price_per_day) < args.days_per_config:
        args.days_per_config = len(eth_price_per_day)
        print("days_per_config supplied was greater than length of price list")

    cdp_rates = [float(cdp_config[2]) * i for i in range(int(cdp_config[0]), int(cdp_config[1]))]
    tx_fees = [float(txf_config[2]) * i for i in range(int(txf_config[0]), int(txf_config[1]))]
    belief_factor = float(config_lines[-1])

    print("Input Parameters for Test")
    print("--investors", args.investors)
    print("--days_per_config", args.days_per_config)
    print("--type", args.type)
    print("--runs", args.runs)
    print("--log", args.log)
    print("--logidr", args.logdir)
    print("--config", args.config)

    run_tests(args.investors, belief_factor, cdp_rates, tx_fees, args.runs, eth_price_per_day, args.days_per_config, args.type,
              args.logdir,
              args.log, sumfile) 
    sumfile.close()

