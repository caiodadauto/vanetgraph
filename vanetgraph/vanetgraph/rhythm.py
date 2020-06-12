import os
import json
import logging
from pathlib import Path

import numpy as np
import pandas as pd
import seaborn as sns
import graph_tool as gt
import matplotlib.pyplot as plt
from tqdm import tqdm
from matplotlib.colors import LogNorm

from .jsons import JsonData
from .utils.constructor import get_metrics


# TODO: Which is  the best bins?
def get_bins(obj_paths, path):
    def save_bins(bin_index, path):
        save_path = path.joinpath("bins.json")
        bins = bin_index.copy()
        for metric in bin_index.keys():
            bins[metric][0] = bins[metric][0].tolist()
        with open(save_path, "w") as f:
            json.dump(bins, f)

    with open(obj_paths[0], 'r') as f:
        obj = json.load(f)
    metrics = list(obj.keys())

    bin_index = {}
    all_metric_values = {}
    for metric in metrics:
        all_metric_values[metric] = []
        bin_index[metric] = []
    for i in tqdm(range(len(obj_paths))):
        obj_path = obj_paths[i]
        with open(obj_path, 'r') as f:
            obj = json.load(f)
        for metric, value in obj.items():
            all_metric_values[metric].append(value)
    for metric, value in all_metric_values.items():
        all_metric_values[metric] = np.array(value).reshape(-1)
        print(all_metric_values[metric])
        bins = np.histogram_bin_edges(all_metric_values[metric], bins='auto', range=(0, all_metric_values[metric].max()))
        bin_index[metric].append(bins)
        index = ["{:.3E}".format(bins[i] + (bins[i + 1] - bins[i]) / 2) for i in range(0, len(bins) - 1)]
        index.reverse()
        bin_index[metric].append(index)
    print("Tis is the  computed bins ", bin_index)
    save_bins(bin_index, path)
    quit()
    return bin_index

def create_gvr(arr, save_micro, times, bins, index):
    columns = []
    all_x = np.concatenate(arr)
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
        for metric, value in obj["macro"].items():
            # TODO: Delete file before appending
            with open(save_macro.joinpath(metric + ".dat"), "a") as f:
                f.write("{:.5f}\n".format(value))
        for metric, value in obj["micro"].items():
            if not metric in arr_gvr:
                arr_gvr[metric] = []
            arr_gvr[metric].append(np.array(value))
    for metric in arr_gvr.keys():
        if not os.path.isdir(save_micro.joinpath(metric)):
            os.makedirs(save_micro.joinpath(metric))
    for metric, arr in arr_gvr.items():
        create_gvr(arr, save_micro.joinpath(metric), times, bin_index[metric][0], bin_index[metric][1])

# FIXME: There is some strange in the genrated image (the oder is wrong!)
def process_gvr(rootdir, window_size, savedir, metrics=None, from_graph=False):
    rootdir = Path(rootdir)
    savedir = Path(savedir)
    if from_graph:
        json_data = JsonData(rootdir)
        if metrics == None or metrics == []:
            print("The list of metrics is empty.")
            exit(1)
        else:
            obj_paths = json_data.create_jsons_from_graphs(metrics)
            quit()
    else:
        obj_paths = sorted(rootdir.glob("*.json"), key=lambda x: int(x.stem))

    objs = []
    times = []
    bin_index = get_bins(obj_paths, savedir)
    for i in tqdm(range(len(obj_paths))):
        obj_path = obj_paths[i]
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
