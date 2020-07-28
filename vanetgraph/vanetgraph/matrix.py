import os
import json

import numpy as np
from tqdm import tqdm
from pathlib import Path


def process_csv(load_path):
    save_path = load_path.parent.joinpath("data_csv")
    json_paths = sorted(load_path.glob("*.json"), key=lambda x: int(x.stem))
    if not os.path.isdir(save_path):
        os.makedirs(save_path)

    n_labels = 0
    n_jsons = len(json_paths)
    print("Getting the maximum label")
    for i in tqdm(range(n_jsons)):
        with open(json_paths[i], "r") as f:
            obj = json.load(f)
        l = max(map(int, obj["labels"]))
        if l > n_labels:
            n_labels = l
    n_labels += 1

    with open(json_paths[0], "r") as f:
        metrics = list(json.load(f)["micro"].keys())

    for m in metrics:
        with open(save_path.joinpath(m + ".csv"), "w") as fcsv:
            fcsv.write("time" + ",")
            for i in range(n_labels - 1):
                fcsv.write(str(i) + ",")
            fcsv.write(str(n_labels - 1) + "\n")

    for m in metrics:
        with open(save_path.joinpath(m + ".csv"), "a") as fcsv:
            for i in tqdm(range(len(json_paths))):
                p = json_paths[i]
                line = np.full(n_labels, -1)
                with open(p, "r") as f:
                    obj = json.load(f)
                graph_labels = obj["labels"]
                metric_values = obj["micro"][m]
                print(graph_labels, metric_values)
                for l, v in zip(graph_labels, metric_values):
                    line[int(l)] = v
                for i in range(n_labels - 1):
                    fcsv.write(str(line[i]) + ",")
                fcsv.write(str(line[n_labels - 1]) + "\n")
    return save_path
