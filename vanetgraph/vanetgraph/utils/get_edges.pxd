# distutils: language = c++

from libcpp.vector cimport vector


cdef extern from "get_edges.cpp":
    pass
cdef extern from "get_edges.h":
    ctypedef struct EdgeProp:
        vector[int] e;
        float w;
    cdef vector[EdgeProp] get_edges( vector[vector[float]] pos, float th, int n_proc );

