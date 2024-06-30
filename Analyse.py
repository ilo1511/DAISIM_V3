import argparse
import pickle
import os
from util import log
import numpy as np
import random
import hashlib

real_dai = np.array([1,1.02,1,1])

def analyse(filename):
    input_file = open(filename, 'rb')
    cdp_axis, txf_axis, run_axis, dai_axis, asset_history, risk_params_axis, herd_params_axis, belief_factor_axis, eth_price_per_day_axis, alpha_axis = pickle.load(input_file)
    data = [cdp_axis, txf_axis, run_axis, dai_axis, asset_history, risk_params_axis, herd_params_axis, belief_factor_axis, eth_price_per_day_axis, alpha_axis]
    
    output_dai = np.array(dai_axis[0])

    error = sum((output_dai - real_dai)**2)
    h_low = np.min(herd_params_axis)
    h_high = np.max(herd_params_axis)
    
    name = int(random.random()*10000000)
    log_filename = 'Analyse/'+ str(name) + '_analysis_log.log'
    
    log(f'error: {error}', log_filename, flag=True)
    log(f'alpha: {alpha_axis[0][0]}', log_filename, flag=True )
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
    
    args = parser.parse_args()
    print(args.data)
    print ("DONE")
    analyse(args.data)