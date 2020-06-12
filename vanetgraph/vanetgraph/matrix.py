import os
import json

import numpy as np
from tqdm import tqdm
from pathlib import Path



def create_csv(load_path):
    save_path = path.parent.joinpath("data_csv")
    json_paths = sorted(load_path.glob("*.json"), key=lambda x: int(x.stem))
    if not os.path.isdir(save_path):
        os.makedirs(save_path)

    with open(load_path.parent.joinpath("labels_translate"), "r") as f:
        labels = list(json.load(f).values())

    with open(json_paths[0], "r") as f:
        metrics = list(json.load(f)["micro"].keys())

    n_labels = len(labels)
    for m in metrics:
        with open(save_path.joinpath(m + ".csv"), w) as fcsv:
            fcsv.write("time" + ",")
            for i in range(n_labels - 1):
                fcsv.write(str(labels[i]) + ",")
            fcsv.write(str(labels[n_labels - 1]) + "\n")
    labels.clear()

    for m in metrics:
        with open(save_path.joinpath(m + ".csv"), a) as fcsv:
            for i in tqdm(range(len(json_paths))):
                p = json_paths[i]
                line = np.full(n_labels, -1)
                with open(p, "r") as f:
                    obj = json.load(f)
                graph_labels = obj["labels"]
                metric_values = obj["micro"][m]
                for l, v in zip(graph_labels, metric_values):
                    line[l] = v
                for i in range(n_labels - 1):
                    fcsv.write(str(line[i]) + ",")
                fcsv.write(str(line[n_labels - 1]) + "\n")
    return save_path
