import argparse
from pathlib import Path

from vanetgraph import process_gvr, process_csv, create_jsons_from_graphs, create_data_nx

def metrics(s):
    try:
        l = s.split(',')
        return l
    except:
        raise argparse.ArgumentTypeError("Metrics must be a sequence of strings splited by commas.")

def run(root_path, window_size, metrics, from_jsons, create_rhythms, non_nx_convert, last_time):
    rootdir = Path(root_path)
    savedir = rootdir.parent
    if from_jsons:
        obj_paths = sorted(rootdir.glob("*.json"), key=lambda x: int(x.stem))
    else:
        if metrics == None or metrics == []:
            print("The list of metrics is empty.")
            exit(1)
        elif create_rhythms:
            obj_paths = create_jsons_from_graphs(rootdir, metrics)
    if create_rhythms:
        process_gvr(savedir, obj_paths, window_size)
    if not non_nx_convert:
        create_data_nx(rootdir, metrics, last_time)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("root_path", type=str, help="Path to the target assets")
    p.add_argument("--last-time", type=int, default=-1, help="Last processed time")
    p.add_argument("--window-size", type=int, default=120, help="Window size to create graph rhythms")
    p.add_argument("--metrics", type=metrics, default=["d", "dgc", "cnw"], help="Matrics to be computed")
    p.add_argument("--from-jsons", action="store_true", help="Indicate that the graph rhythms will be created from json files")
    p.add_argument("--non-nx-convert", action="store_true", help="Indicate that the graph will not be converted to networkx format")
    p.add_argument("--create-rhythms", action="store_true", help="Indicate it will be create rhythms dataset")

    args = p.parse_args()
    run(**vars(args))
