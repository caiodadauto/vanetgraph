import argparse
import vanetgraph as vg

def metrics(s):
    try:
        l = s.split(',')
        return l
    except:
        raise argparse.ArgumentTypeError("Metrics must be a sequence of strings splited by commas.")

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    # Stting environment
    p.add_argument("raw_file_path", type=str, help="Path to raw file for graphs")
    p.add_argument("--graph-root", type=str, default="graphs/",
                   help="Directory where graphs will be saved")
    p.add_argument("--transmission-range", type=float, default=200.0, help="Maximum range for transmission")
    p.add_argument("--metrics", type=metrics, default=["d", "dc", "pgr"], help="Matrics to be computed")
    p.add_argument("--last-read-time", type=int, default=-1, help="Time in until the graphs already been processed")
    p.add_argument("--n-proc", type=int, help="Number of threads to be used in the OpenMP")

    args = p.parse_args()
    vg.parser(**vars(args))
