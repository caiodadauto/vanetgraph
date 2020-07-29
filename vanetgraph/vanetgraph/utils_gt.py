import os

import numpy as np
import networkx as nx
import graph_tool as gt
from tqdm import tqdm
from pathlib import Path

from .utils.constructor import get_metric_value


def nodes_for_adding(num_nodes, labels, pos, speed, kwmetrics_node, names_translate):
    out = []
    keys = list(kwmetrics_node.keys())
    for n in range(num_nodes):
        dict_par = {
            "label": labels[n],
            "pos": pos[:, n].reshape(-1),
            "speed": speed[n],
        }
        for k in keys:
            dict_par[names_translate[k]] = kwmetrics_node[k][n]
        out.append((n, dict_par))
    return out


def convert_gt_to_nx(gt_path, metrics):
    G = nx.Graph()
    ggt = gt.load_graph(str(gt_path))

    names_translate = {
        "dg": "degree",
        "dgc": "degree_centrality",
        "cnw": "cluster_nw",
        "cw": "cluster_w",
        "pgr": "page_range",
        "d": "density"
    }

    num_edges = ggt.num_edges()
    num_nodes = ggt.num_vertices()
    kwmetrics_node = {}
    kwmetrics_global = {}
    for m in metrics:
        value = get_metric_value( ggt, num_nodes, num_edges, m )
        if isinstance(value, list):
            kwmetrics_node[m] = value
        else:
            kwmetrics_global[m] = value

    time = gt_path.stem.split(".")[0]
    save_path = gt_path.parent.joinpath("../data_nx")
    if not os.path.isdir(save_path):
        os.makedirs(save_path)

    edges = ggt.get_edges([ggt.ep.weight])
    G.add_weighted_edges_from(edges)
    G = nx.convert_node_labels_to_integers(G)

    labels = ggt.vp.label.get_2d_array([0])[0]
    pos = ggt.vp.pos.get_2d_array([0,1])
    speed = ggt.vp.speed.get_array()
    nodes_dict = nodes_for_adding(num_nodes, labels, pos, speed, kwmetrics_node, names_translate)
    G.add_nodes_from(nodes_dict)

    G.graph["time"] = int(time)
    for m, value in kwmetrics_global.items():
        G.graph[names_translate[m]] = value

    diG = nx.to_directed(G)
    nx.write_gpickle(diG, save_path.joinpath("{}.gpickle".format(time)))


def create_data_nx(paths, metrics):
    graph_paths = sorted(paths.glob("*.gt.xz"), key=lambda x: int(x.stem.split(".")[0]))
    print("Converting graph_tool to networkx with metrics")
    for i in tqdm(range(len(graph_paths))):
        convert_gt_to_nx(graph_paths[i], metrics)
