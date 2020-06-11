import os
import json
import logging
from pathlib import Path

import numpy as np
import pandas as pd
import seaborn as sns
import graph_tool as gt
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from .utils.constructor import get_metrics


def create_jsons_from_graphs(path, metrics):
    save_path = path.parent.joinpath("metric_jsons")
    if not os.path.isdir(save_path):
        os.makedirs(save_path)

    graph_paths = sorted(path.glob("*.gt.xz"), key=lambda x: int(x.stem.split(".")[0]))
    for p in graph_paths:
        G = gt.load_graph(str(p))
        get_metrics(G, G.num_vertices(), G.num_edges(), int(p.stem.split(".")[0]), str(save_path), metrics)
    return sorted(save_path.glob("*.json"), key=lambda x: int(x.stem))

def get_bins(obj_paths, metrics):
    for obj_path in obj_paths:
        with open(obj_path, 'r') as f:
            obj = json.load(f)
        bin_index = {}
        all_metric_values = {}
        for metric in obj.keys():
            all_metric_values[metric] = []
            bin_index[metric] = []
        for metric, value in obj.items():
            all_metric_values[metric].append(value)
        for metric, value in all_metric_values.items():
            all_metric_values[metric] = np.array(value).reshape(-1)
            bins = np.histogram_bin_edges(all_metric_values[metric], bins='auto', range=(0, all_metric_values[metric].max()))
            bin_index[metric].append(bins)

            index = ["{:.3E}".format(bins[i] + (bins[i + 1] - bins[i]) / 2) for i in range(0, len(bins) - 1)]
            index.reverse()
            bin_index[metric].append(index)
        return bin_index

# TODO: Which is  the best bins?
def create_gvr(arr, save_micro, times, bins, index):
    columns = []
    all_x = np.concatenate(arr)
    # bins = np.histogram_bin_edges(all_x, bins='auto', range=(0, all_x.max()))
    for x in arr:
        n_nodes = len(x)
        x_hist, _ = np.histogram(x, bins, range=(0, all_x.max()), weights=np.full(n_nodes, 1 / n_nodes))
        columns.append(x_hist[::-1])
    raw_gvr = np.stack(columns, axis=1)
    df_gvr = pd.DataFrame(np.log10(raw_gvr + 1), columns=times, index=index)
    sns.heatmap(df_gvr, vmax=np.log10(2), cbar=False)
    plt.savefig(save_micro.joinpath(str(times[-1]) + ".jpg"), dpi=80)
    plt.close()

def parse_objs(objs, savedir, times, bin_index):
    save_macro = savedir.joinpath('macro')
    save_micro = savedir.joinpath('micro')
    if not os.path.isdir(save_macro):
        os.makedirs(save_macro)
    if not os.path.isdir(save_micro):
        os.makedirs(save_micro)
    arr_gvr = {}
    for obj in objs:
        for metric, value in obj.items():
            if isinstance(value, (int, float)):
                # TODO: Delete file before appending
                with open(save_macro.joinpath(metric + ".dat"), "a") as f:
                    f.write("{:.5f}\n".format(value))
            else:
                if not metric in arr_gvr:
                    arr_gvr[metric] = []
                arr_gvr[metric].append(np.array(value))
    for metric in arr_gvr.keys():
        if not os.path.isdir(save_micro.joinpath(metric)):
            os.makedirs(save_micro.joinpath(metric))
    for metric, arr in arr_gvr.items():
        create_gvr(arr, save_micro.joinpath(metric), times, bin_index[metric][0], bin_index[metric][1])

def process_gvr(rootdir, window_size, savedir, metrics=None, from_graph=False):
    rootdir = Path(rootdir)
    savedir = Path(savedir)
    if from_graph:
        if metrics == None or metrics == []:
            print("The list of metrics is empty.")
            exit(1)
        else:
            obj_paths = create_jsons_from_graphs(rootdir, metrics)
    else:
        obj_paths = sorted(rootdir.glob("*.json"), key=lambda x: int(x.stem))

    objs = []
    times = []
    bin_index = get_bins(obj_paths, metrics)
    for obj_path in obj_paths:
        with open(obj_path, 'r') as f:
            obj = json.load(f)
        objs.append(obj)
        times.append(int(obj_path.stem))
        if len(objs) > window_size:
            _ = objs.pop(0)
            _ = times.pop(0)
        if len(objs) == window_size:
            print(times)
            parse_objs(objs, savedir, times, bin_index)
