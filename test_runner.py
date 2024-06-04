import os
import argparse

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

    config_lst.remove(".DS_Store")  
    config_lst.remove("Fact_config.config")
      
    for config in config_lst:
        print("Running Test with config", config)
        log_subdir = config[:-7]
        print(config)
        print(args.configdir)
        os.system("python3 sim.py --config " + os.path.join(args.configdir, config) + " --logdir " + os.path.join(args.logdir,log_subdir) + " --days_per_config 1")
        os.system("python3 plot_gen.py --data " + os.path.join(args.logdir, log_subdir, "sim-summary.pickle"))





