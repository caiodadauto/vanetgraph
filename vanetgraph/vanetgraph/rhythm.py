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


def get_metrics(path, metrics):
    print("TODO")
    exit(0)

# TODO: Which is  the best ybins?
def create_gvr(arr, save_micro, times, resolution=0.00001):
    columns = []
    all_x = np.concatenate(arr)
    ybins = int((all_x.max() // resolution)) + 1
    max_x = ybins * resolution
    for x in arr:
        n_nodes = len(x)
        x_hist, _ = np.histogram(x, ybins, range=(0, max_x), weights=np.full(n_nodes, 1 / n_nodes))
        columns.append(x_hist[::-1])
    index = ["{:.4f}".format(v) for i, v in enumerate(np.arange(0, max_x, resolution / 2)) if (i + 1) % 2 == 0]
    index.reverse()
    raw_gvr = np.stack(columns, axis=1)
    df_gvr = pd.DataFrame(np.log10(raw_gvr + 1), columns=times, index=index)
    sns.heatmap(df_gvr, vmax=np.log10(2), cbar=False)
    plt.savefig(save_micro.joinpath(str(times[-1]) + ".jpg"), dpi=80)
    plt.close()

def parse_objs(objs, savedir, times):
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
        create_gvr(arr, save_micro.joinpath(metric), times)

def process_gvr(rootdir, window_size, savedir, metrics=None, from_graph=False):
    rootdir = Path(rootdir)
    savedir = Path(savedir)
    if from_graph:
        if metrics == None or metrics == []:
            print("The list of metrics is empty.")
            exit(1)
        else:
            obj_paths = sorted(rootdir.glob("*.gt.xz"), key=lambda x: int(x.stem))
    else:
        obj_paths = sorted(rootdir.glob("*.json"), key=lambda x: int(x.stem))

    objs = []
    times = []
    for obj_path in obj_paths:
        if from_graph:
            obj = get_metrics(obj_path, metrics)
        else:
            with open(obj_path, 'r') as f:
                obj = json.load(f)
        objs.append(obj)
        times.append(int(obj_path.stem))
        if len(objs) > window_size:
            _ = objs.pop(0)
            _ = times.pop(0)
        if len(objs) == window_size:
            parse_objs(objs, savedir, times)
