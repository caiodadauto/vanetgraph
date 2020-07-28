import os

import graph_tool as gt
from tqdm import tqdm
from pathlib import Path

from .utils.constructor import get_metrics


def create_jsons_from_graphs(path, metrics):
    load_path = path
    save_path = path.parent.joinpath("metric_jsons")
    if not os.path.isdir(save_path):
        os.makedirs(save_path)

    graph_paths = sorted(load_path.glob("*.gt.xz"), key=lambda x: int(x.stem.split(".")[0]))
    print("Process graphs to create JSONs")
    for i in tqdm(range(len(graph_paths))):
        p = graph_paths[i]
        G = gt.load_graph(str(p))
        labels = G.vp.label.get_2d_array([0]).tolist()[0]
        get_metrics(G, G.num_vertices(), G.num_edges(), int(p.stem.split(".")[0]), str(save_path), metrics, labels)
    return sorted(save_path.glob("*.json"), key=lambda x: int(x.stem))
