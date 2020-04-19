#ifndef _GET_EDGES_H
#define _GET_EDGES_H

#include <vector>

typedef struct EdgeProp
{
    std::vector<int> e;
    float w;
} EdgeProp;

std::vector<EdgeProp> get_edges(const std::vector<std::vector<float>> pos, const float th, const int n_proc);

#endif
