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
    
    print(dai_axis)
    output_dai = np.array(dai_axis[0])
    print (output_dai)
    error = sum((output_dai - real_dai)**2)
    
    name = int(random.random()*10000000)
    print(name)
    log_filename = 'Analyse/'+ str(name) + '_analysis_log.log'
    
    for value_list in data:
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