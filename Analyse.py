import argparse
import pickle
import os
import numpy as np
import pandas as pd
from util import log

real_dai = np.array([
    1.0060445265046256,
    0.9991222915044283,
    1.0050328043302443,
    0.9969789216188777,
    0.9888977681277664,
    0.986556026998058,
    1.004015281990389,
    0.9945960976838956,
    1.001086653565765,
    0.9985420059997772,
    1.0011374006732177,
    0.9944209489772055,
    0.9942691001257494,
    0.993309360008666,
    0.9954298052411727
    ])

def analyse(filename, analysedir, logdir):
    with open(filename, 'rb') as input_file:
        cdp_axis, txf_axis, run_axis, dai_axis, asset_history, risk_params_axis, herd_params_axis, belief_factor_axis, eth_price_per_day_axis, alpha_1_axis, alpha_2_axis = pickle.load(input_file)
        
    output_dai = np.array(dai_axis[0])
    correlation = np.corrcoef(dai_axis,real_dai)
    mse = np.square(np.subtract(dai_axis, real_dai.mean()))
    rmse = np.sqrt(mse)
    h_low = np.min(herd_params_axis)
    h_high = np.max(herd_params_axis)
    alpha_1 = alpha_1_axis[0][0]
    alpha_2 = alpha_2_axis[0][0]
    belief = belief_factor_axis[0]

    log_filename = os.path.join(analysedir, f"{os.path.basename(logdir)}_Analyse_output.txt")
    
    error = 0.4*(1-correlation) + 0.6*rmse
    
    log(f'rmse: {rmse}',log_filename, flag=True)
    log(f'correlation: {correlation}',log_filename, flag=True)
    log(f'error: {error}', log_filename, flag=True)
    log(f'alpha_1: {alpha_1}', log_filename, flag=True)
    log(f'alpha_2: {alpha_2}', log_filename, flag=True)
    log(f'h_low: {h_low}', log_filename, flag=True)
    log(f'h_high: {h_high}', log_filename, flag=True)
    log(f'belief_factor: {belief}', log_filename, flag=True)

    for value_list in [dai_axis]:
        for value in value_list:
            log(f'{value}', log_filename, flag=True)
            
    # Check if the dataframe already exists
    if os.path.exists('experiment_data.csv'):
        df = pd.read_csv('experiment_data.csv')
    else:
        df = pd.DataFrame(columns=['belief', 'h_low', 'h_high', 'alpha_1', 'alpha_2', 'error'])

    # Create a new row for the current experiment
    new_row = pd.DataFrame({'belief': [belief], 'h_low': [h_low], 'h_high': [h_high], 'alpha_1': [alpha_1], 'alpha_2': [alpha_2], 'error': [error]})

    # Append the new row to the dataframe
    df = pd.concat([df, new_row], ignore_index=True)

    # Save the updated dataframe to a csv file
    df.to_csv('experiment_data.csv', index=False)

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
        "--logdir",
        type=str,
        default="sim-logs",
        help="Log Directory"
    )

    args = parser.parse_args()
    analyse(args.data, args.analysedir, args.logdir)
