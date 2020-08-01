import os

import numpy as np
import graph_tool as gt
from tqdm import tqdm
from pathlib import Path
from graph_tool.centrality import pagerank
from graph_tool.clustering import local_clustering


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

def add_metrics(graph_path, metrics):
    def get_metric(ggt, metric, n_nodes, n_edges):
        if "d" == metric:
            # Density
            if n_nodes <= 1:
                value = 0.0
            else:
                value = ( 2.0 * n_edges ) / ( n_nodes * (n_nodes - 1.0) )
            ggt.gp[metric] = ggt.new_gp("float", val=value)
        elif "dg" == metric:
            # Degree
            if n_nodes <= 1:
                value = np.zeros(n_nodes, dtype=np.float32)
            else:
                value = ggt.degree_property_map('total').get_array()
            ggt.vp[metric] = ggt.new_vp("double", vals=value)
        elif "dgc" == metric:
            # Degree centrality
            if n_nodes <= 1:
                value = np.zeros(n_nodes, dtype=np.float32)
            else:
                value = ggt.degree_property_map('total').get_array() / (n_nodes - 1.0)
            ggt.vp[metric] = ggt.new_vp("double", vals=value)
        elif "cnw" == metric:
            # Clustering coefficient ( non-weighted )
            value = local_clustering(ggt).get_array()
            ggt.vp[metric] = ggt.new_vp("double", vals=value)
        elif "cw" == metric:
            # Clustering coefficient ( weighted )
            value = local_clustering(ggt, weight=ggt.ep.weight).get_array()
            ggt.vp[metric] = ggt.new_vp("double", vals=value)
        elif "pgr" == metric:
            # Page Rank
            value = pagerank(ggt).get_array()
            ggt.vp[metric] = ggt.new_vp("double", vals=value)

    ggt = gt.load_graph(str(graph_path))
    time = int(graph_path.stem.split(".")[0])
    ggt.gp.time = ggt.new_gp("int32_t", val=time)

    save_path = graph_path.parent.joinpath("../graphs_with_metrics")
    if not os.path.isdir(save_path):
        os.makedirs(save_path)

    num_edges = ggt.num_edges()
    num_nodes = ggt.num_vertices()
    for m in metrics:
        get_metric(ggt, m, num_nodes, num_edges)

    ggt.save(str(save_path.joinpath("{}.gt.xz".format(time))))


# def convert_gt_to_nx(gt_path, metrics):
#     G = nx.Graph()
#     ggt = gt.load_graph(str(gt_path))

#     names_translate = {
#         "dg": "degree",
#         "dgc": "degree_centrality",
#         "cnw": "cluster_nw",
#         "cw": "cluster_w",
#         "pgr": "page_range",
#         "d": "density"
#     }

#     num_edges = ggt.num_edges()
#     num_nodes = ggt.num_vertices()
#     kwmetrics_node = {}
#     kwmetrics_global = {}
#     for m in metrics:
#         value = get_metric_value( ggt, num_nodes, num_edges, m )
#         if isinstance(value, list):
#             kwmetrics_node[m] = value.copy()
#         else:
#             kwmetrics_global[m] = value
#         del(value)

#     time = gt_path.stem.split(".")[0]
#     save_path = gt_path.parent.joinpath("../data_nx")
#     if not os.path.isdir(save_path):
#         os.makedirs(save_path)

#     edges = ggt.get_edges([ggt.ep.weight])
#     G.add_weighted_edges_from(edges)
#     G = nx.convert_node_labels_to_integers(G)

#     labels = ggt.vp.label.get_2d_array([0])[0]
#     pos = ggt.vp.pos.get_2d_array([0,1])
#     speed = ggt.vp.speed.get_array()
#     nodes_dict = nodes_for_adding(num_nodes, labels, pos, speed, kwmetrics_node, names_translate)
#     G.add_nodes_from(nodes_dict)

#     G.graph["time"] = int(time)
#     for m, value in kwmetrics_global.items():
#         G.graph[names_translate[m]] = value

#     diG = nx.to_directed(G)
#     # with bz2.BZ2File(save_path.joinpath("{}.gpickle.bz2".format(time)), "w") as f:
#     with bz2.BZ2File("/home/caio/{}.gpickle.bz2".format(time), "w") as f:
#         pickle.dump(diG, f)


def create_data_nx(paths, metrics, last_time=-1):
    gt.openmp_set_num_threads(gt.openmp_get_num_threads())
    graph_paths = sorted(paths.glob("*.gt.xz"), key=lambda x: int(x.stem.split(".")[0]))
    print("Adding metrics to the graphs")
    for i in tqdm(range(len(graph_paths))):
        time = int(graph_paths[i].stem.split(".")[0])
        if time > last_time:
            add_metrics(graph_paths[i], metrics)
