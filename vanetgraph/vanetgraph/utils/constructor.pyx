# distutils: language = c++

import os
import json
import numpy as np
import graph_tool as gt
from graph_tool.centrality import pagerank
from graph_tool.clustering import local_clustering

cimport cython
cimport numpy as np
from libcpp.vector cimport vector
from get_edges cimport get_edges, EdgeProp


# cdef np.ndarray[np.int_t, ndim=2] edges_vec_to_np(vec):
#     cdef int [:, :] vec_np = np.zeros((vec.size(), 2), dtype=np.int)
#     cdef int size = vec.size();
#     for i in range(size):
#         for j in range(2):
#             vec_np[i][j] = vec[i][j]
#     return vec_np

# cdef vector[vector[float]] pos_np_to_vec(np.ndarray[np.float32_t, ndim=2] vec_np):
#     cdef vector[vector[float]] vec
#     for i in range(vec_np.shape[0]):
#         vec.push_back([vec_np[i][0], vec_np[i][1]])
#     return vec

@cython.boundscheck(False)
@cython.wraparound(False)
cpdef create_graph( np.ndarray[np.float32_t, ndim=2] pos, np.ndarray[np.float32_t, ndim=1] speed,
                    list label, list metrics, int n_proc, float th, str path, int time ):
    cdef int i
    cdef int n_edges
    cdef int n_nodes = pos.shape[0]
    # cdef double density
    cdef vector[EdgeProp] edges_p
    # cdef vector[double] page_rank
    # cdef vector[double] degree_centrality

    gt.openmp_set_num_threads(n_proc)

    G = gt.Graph(directed=False)
    G.add_vertex(n_nodes)
    G.vp.label = G.new_vp("string", vals=label)
    G.vp.pos = G.new_vp("vector<float>", vals=pos)
    G.vp.speed = G.new_vp("float", vals=speed)

    edges_p = get_edges(pos, th, n_proc)
    n_edges = edges_p.size()
    edges = np.zeros((n_edges, 2), dtype=np.intc)
    weights = np.zeros(n_edges, dtype=np.float32)
    for i in range(n_edges):
        edges[i][0] = edges_p[i].e[0]
        edges[i][1] = edges_p[i].e[1]
        weights[i] = edges_p[i].w
    G.add_edge_list(edges)
    G.ep.weight = G.new_ep("float", vals=weights)
    G.save(os.path.join(path, "{}.gt.xz".format(time)))

    get_metrics( G, n_nodes, n_edges, time, path, metrics )

@cython.boundscheck(False)
@cython.wraparound(False)
cpdef get_metrics( object G, int n_nodes, int n_edges, int time, str path, list metrics, short save_json=True ):
    dict_metrics = {}
    # Density
    if "d" in metrics:
        if n_nodes <= 1:
            density = 0.0
        else:
            density = ( 2.0 * n_edges ) / ( n_nodes * (n_nodes - 1.0) )
        dict_metrics["density"] = density

    # Degree
    if "dg" in metrics:
        if n_nodes <= 1:
            degree = np.zeros(n_nodes, dtype=np.float64)
        else:
            degree = G.degree_property_map('total').get_array().tolist()
        dict_metrics["degree"] = degree

    # Degree centrality
    if "dgc" in metrics:
        if n_nodes <= 1:
            degree_centrality = np.zeros(n_nodes, dtype=np.float64)
        else:
            degree_centrality = ( G.degree_property_map('total').get_array() / <double>(n_nodes - 1.0) ).tolist()
        dict_metrics["degree_centrality"] = degree_centrality

    # Clustering coefficient ( non-weighted )
    if "cnw" in metrics:
        cluster_nw = local_clustering(G).get_array().tolist()
        dict_metrics["cluster_nw"] = cluster_nw

    # Clustering coefficient ( weighted )
    if "cw" in metrics:
        cluster_w = local_clustering(G, weight=G.ep.weight).get_array().tolist()
        dict_metrics["cluster_w"] = cluster_w

    # Page Rank
    if "pgr" in metrics:
        page_rank = pagerank(G).get_array().tolist()
        dict_metrics["page_range"] = page_rank

    if save_json:
        with open(os.path.join(path, "{}.json".format(time)), "w") as f:
            json.dump(dict_metrics, f)
