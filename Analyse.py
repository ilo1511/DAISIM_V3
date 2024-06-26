import argparse
import pickle
import os
from util import log
import numpy as np
import random
import hashlib

real_dai = np.array([1,1.02,1,1])

def analyse(filename, counter):
    input_file = open(filename, 'rb')
    cdp_axis, txf_axis, run_axis, dai_axis, asset_history, risk_params_axis, herd_params_axis, belief_factor_axis, eth_price_per_day_axis, alpha_1_axis, alpha_2_axis = pickle.load(input_file)
    data = [cdp_axis, txf_axis, run_axis, dai_axis, asset_history, risk_params_axis, herd_params_axis, belief_factor_axis, eth_price_per_day_axis, alpha_1_axis, alpha_2_axis]
    
    output_dai = np.array(dai_axis[0])

    error = sum((output_dai - real_dai)**2)
    h_low = np.min(herd_params_axis)
    h_high = np.max(herd_params_axis)
    
    log_filename = f'Analyse/{counter}_analysis_log.log'
        
    log(f'error: {error}', log_filename, flag=True)
    log(f'alpha_1: {alpha_1_axis[0][0]}', log_filename, flag=True )
    log(f'alpha_2: {alpha_2_axis[0][0]}', log_filename, flag=True )

        # Log h_low and h_high

    log(f'h_low: {h_low}', log_filename, flag=True)
    log(f'h_high: {h_high}', log_filename, flag=True)
    
    # Log herd_params_axis and alpha_axis
    for value_list in [dai_axis]:
        for value in value_list:
            log(f'{value}', log_filename, flag=True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='MAKER Sim Plotter CLI')

    parser.add_argument(
        "--data",
        type=str,
        default="",
        required=True,
        help="Path to a sim-summary.pickle"
        
    )
    
    parser.add_argument(
        "--analysedir",
        type=str,
        default="",
        required=True,
        help="Path to a directory for analysis files"
        
    )
    
    parser.add_argument(
        "--counter",
        type=int,
        default=0,
        required=True,
        help="Counter to give name to analyse file"
    )
    
    args = parser.parse_args()
    analyse(args.data, args.counter)