import os
import argparse
import subprocess

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Test Runner CLI')

    parser.add_argument(
        "--logdir",
        type=str,
        default="",
        required=True,
        help="Log directory directory"
    )

    parser.add_argument(
        "--configdir",
        type=str,
        default="",
        required=True,
        help="Path to config directory"
    )

    args = parser.parse_args()

    print("Initializing Test Runner")
    os.makedirs(args.logdir, exist_ok=True)

    config_lst = []
    for config in os.listdir(args.configdir):
        config_lst.append(config)
    
    if ".DS_Store" in config_lst:
        config_lst.remove(".DS_Store")
    if "Fact_config.config" in config_lst:
        config_lst.remove("Fact_config.config")
      
    for config in config_lst:
        print("Running Test with config", config)
        log_subdir = config[:-7]
        config_path = os.path.join(args.configdir, config)
        log_path = os.path.join(args.logdir, log_subdir)
        
        print(config)
        print(args.configdir)
        
        # Running sim.py
        sim_command = [
            "python3", "sim.py",
            "--config", config_path,
            "--logdir", log_path,
            "--days_per_config", "1"
        ]
        subprocess.run(sim_command)
        
        print("BOOM")
        
        # Running plot_gen.py
        ##plot_command = [
        ##    "python3", "plot_gen.py",
        ##    "--data", os.path.join(log_path, "sim-summary.pickle")
        ##]
        ##subprocess.run(plot_command)
        print(log_path)
        print(args.logdir)
        analyse_command = [
            "python3", "Analyse.py", "--data", os.path.join(log_path, "sim-summary.pickle"), "--analysedir", "/Users/heloisegaspard/Desktop/THESIS/DAISIM_V3/Analyse"
        ]
        subprocess.run(analyse_command)