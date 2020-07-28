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

from .utils.constructor import get_metrics


# TODO: Which is  the best bins?
def get_bins(obj_paths, path):
    with open(obj_paths[0], 'r') as f:
        obj = json.load(f)
    metrics = list(obj["micro"].keys())

    bins = {}
    bin_indices = {}
    for metric in metrics:
        bins[metric] = []
        bin_indices[metric] = []
    for i in tqdm(range(len(obj_paths))):
        obj_path = obj_paths[i]
        with open(obj_path, 'r') as f:
            obj = json.load(f)
        for metric, values in obj["micro"].items():
            b = np.histogram_bin_edges(values, bins='auto', range=(0, max(values)))
            if len(b) > len(bins[metric]):
                bins[metric] = b
    for metric, values in bins.items():
        index = ["{:.3E}".format(values[i] + (values[i + 1] - values[i]) / 2) for i in range(0, len(values) - 1)]
        index.reverse()
        bin_indices[metric] = np.array(index)
    return bins, bin_indices

def create_gvr(arr, save_micro, times, bins, index):
    columns = []
    all_x = np.concatenate(arr)
    max_value = all_x.max()
    for x in arr:
        n_nodes = len(x)
        mask_idx = bins < max_value
        bins_to_draw = bins[mask_idx]
        if len(bins_to_draw) < 10:
            bins_to_draw = bins[0:11]
            indiex_to_draw = index[0:10]
        else:
            indiex_to_draw = index[mask_idx[:-1]][:-1]
        x_hist, _ = np.histogram(x, bins_to_draw, range=(0, max_value), weights=np.full(n_nodes, 1 / n_nodes))
        columns.append(x_hist[::-1])
    raw_gvr = np.stack(columns, axis=1)
    df_gvr = pd.DataFrame(np.log10(raw_gvr + 1), columns=times, index=indiex_to_draw)
    sns.heatmap(df_gvr, vmax=np.log10(2), cbar=False)
    plt.savefig(save_micro.joinpath(str(times[-1]) + ".jpg"), dpi=80)
    plt.close()

def parse_objs(objs, savedir, times, bins_info):
    save_micro = savedir.joinpath('micro')
    if not os.path.isdir(save_micro):
        os.makedirs(save_micro)
    arr_gvr = {}
    for obj in objs:
        for metric, value in obj["micro"].items():
            if not metric in arr_gvr:
                arr_gvr[metric] = []
            arr_gvr[metric].append(np.array(value))
    for metric in arr_gvr.keys():
        if not os.path.isdir(save_micro.joinpath(metric)):
            os.makedirs(save_micro.joinpath(metric))
    for metric, arr in arr_gvr.items():
        create_gvr(arr, save_micro.joinpath(metric), times, bins_info[0][metric], bins_info[1][metric])

# FIXME: There is something strange in the genrated image (the oder is wrong!)
def process_gvr(savedir, obj_paths, window_size):
    objs = []
    times = []
    bins_info = get_bins(obj_paths, savedir)
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
            parse_objs(objs, savedir, times, bins_info)
