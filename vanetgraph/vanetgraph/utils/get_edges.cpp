#include <cmath>
#include <omp.h>
#include <vector>

#include "get_edges.h"


std::vector<EdgeProp> get_edges(const std::vector<std::vector<float>> pos, const float th, const int n_proc)
{
#pragma omp declare reduction ( merge : std::vector<EdgeProp> : omp_out.insert( omp_out.end(), omp_in.begin(), omp_in.end() ) )
    const int n = pos.size();
    std::vector<EdgeProp> edges_p;
#pragma omp parallel for reduction( merge: edges_p ) num_threads( n_proc )
    for( int i = 0; i < n; i++ ) {
        const std::vector<float> node = pos[i];
        for( int j = i + 1; j < n; j++ ) {
            const std::vector<float> neighbor = pos[j];
            float a = pow( node[0] - neighbor[0], 2 );
            float b = pow( node[1] - neighbor[1], 2 );
            float dist = sqrt( a + b );
            if( dist <= th ) {
                EdgeProp ep;
                std::vector<int> e{i, j};
                ep.e = e;
                ep.w = dist;
                edges_p.push_back(ep);
            }
        }
    }
    return edges_p;
}
