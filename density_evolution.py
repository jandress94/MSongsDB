from db_utils import *
from graph_utils import *
from metrics import *
from scipy import sparse
import random
import math
import snap
from sklearn.cluster import DBSCAN
import numpy as np

def build_orig_mat(years_and_graphs_map, all_vertex_ids, nid_to_index_map):
    allEdges = set()

    for graph in years_and_graphs_map.values():
        for edge in graph.Edges():
            id1 = edge.GetSrcNId()
            id2 = edge.GetDstNId()
            allEdges.add((id1, id2))
            allEdges.add((id2, id1))

    allEdgeList = [elem for elem in allEdges]
    edgeI = [nid_to_index_map[elem[0]] for elem in allEdgeList]
    edgeJ = [nid_to_index_map[elem[1]] for elem in allEdgeList]
    data = [1] * len(allEdgeList)

    return sparse.coo_matrix((data, (edgeI, edgeJ)), shape = (len(all_vertex_ids), len(all_vertex_ids))).tocsr(), allEdges

def get_sim_mat(graph, all_vertex_ids, nid_to_index_map, weight, allEdges):
    i = []
    j = []
    data = []
    edge_sims = {}

    for edgePair in allEdges:
        i.append(nid_to_index_map[edgePair[0]])
        j.append(nid_to_index_map[edgePair[1]])
        if not graph.IsEdge(edgePair[0], edgePair[1]):
            data.append(0)
        elif (edgePair[1], edgePair[0]) in edge_sims:
            data.append(edge_sims[(edgePair[1], edgePair[0])])
        else:
            node1 = graph.GetNI(edgePair[0])
            node2 = graph.GetNI(edgePair[1])
            sameNeighborCount = 0
            for neighborNId in node1.GetOutEdges():
                if neighborNId != node2.GetId() and graph.IsEdge(node2.GetId(), neighborNId):
                    sameNeighborCount += 1
            if sameNeighborCount != 0:
                sim = 1.0 * weight * sameNeighborCount / math.sqrt((node1.GetDeg() - 1) * (node2.GetDeg() - 1))
            else:
                sim = 0
            data.append(sim)
            edge_sims[edgePair] = sim
    return sparse.coo_matrix((data, (i, j)), shape = (len(all_vertex_ids), len(all_vertex_ids))).tocsr()

def compute_clusters(years_and_weights_map, years_and_graphs_map, year_true):
    # get the set of all vertices across these years
    all_vertices = set()
    for year in years_and_graphs_map:
        all_vertices.update([node.GetId() for node in years_and_graphs_map[year].Nodes()])

    all_vertex_ids = [nid for nid in all_vertices]
    nid_to_index_map = {all_vertex_ids[index] : index for index in range(len(all_vertex_ids))}

    weighted_dist_mat, allEdges = build_orig_mat(years_and_graphs_map, all_vertex_ids, nid_to_index_map)

    for year in years_and_graphs_map:
        weighted_dist_mat -= get_sim_mat(years_and_graphs_map[year], all_vertex_ids, nid_to_index_map, years_and_weights_map[year], allEdges)

    print 'Computing clusters'
    db = DBSCAN(metric='precomputed', eps = 0.84, min_samples = 2).fit(weighted_dist_mat)

    labels = db.labels_
    clusters_map = {}

    notInCluster = 0
    nodes_not_in_clusters = set()
    for node in years_and_graphs_map[0].Nodes():
        label = labels[nid_to_index_map[node.GetId()]]
        if label == -1:
            notInCluster += 1
            nodes_not_in_clusters.add(node.GetId())
        else:
            if label not in clusters_map:
                clusters_map[label] = snap.TIntV()
            clusters_map[label].Add(node.GetId())

    # label all of the nodes not in a cluster, but keep them in their own set
    new_labels = {}
    for node_id in nodes_not_in_clusters:
        node = years_and_graphs_map[0].GetNI(node_id)
        neighbor_cluster_counter = {cluster_id : 0 for cluster_id in clusters_map.keys()}
        for neighbor_id in node.GetOutEdges():
            if labels[nid_to_index_map[neighbor_id]] != -1:
                neighbor_cluster_counter[labels[nid_to_index_map[neighbor_id]]] += 1
        max_count = max(neighbor_cluster_counter.values())
        new_labels[node_id] = random.choice([cluster_id for cluster_id in neighbor_cluster_counter.keys() if neighbor_cluster_counter[cluster_id] == max_count])

    # put the newly assigned nodes into the real clusters
    for node_id in new_labels:
        clusters_map[new_labels[node_id]].Add(node_id)

    # Convert to expected format
    clusters = snap.TCnComV()
    for cluster in clusters_map.values():
        clusters.Add(snap.TCnCom(cluster))

    return clusters, 1.0 * notInCluster / years_and_graphs_map[0].GetNodes()


db_filename = 'D:/artist_full.db'

# This is what determines the years which are averaged together, 
# and the relative weights used in the edge interpolation.
# A value of {-1: 0.5, 0: 0.5} means that the edge weights for the
# current year should be half the edge weights from that current year's graph (the key of 0)
# and half the edge weights from the previous year's graph (the key of -1)
# NOTE: you need to include all consecutive integers from the min year to max,
# even if that means just giving some weight 0
years_and_weights_map = {-1: 0.5, 0: 0.5}
years_and_graphs_map = {}

conn = open_db_conn(db_filename)

artist_id_to_int, nid_to_aid_map = get_id_mapping(conn)

start_year = 2000
end_year = 2010

year_range = range(start_year - 1, end_year + 1)

years = []
my_modularity_list = []
term_metric_list = []
temp_smoothness_list = []
num_clusters = []
percentsNotInClusters = []

CmtyV_t_minus_1 = None

for year in year_range:
    print 'Building graph for', year
    graph = build_graph(conn, year, artist_id_to_int)

    if graph.GetNodes() == 0:
        print 'hit the end'
        break

    # if this is the beginning and we're still computing the original few graphs...
    if len(years_and_graphs_map) < len(years_and_weights_map):
        minNotFount = float('inf')
        for key in years_and_weights_map:
            if key not in years_and_graphs_map and key < minNotFount:
                minNotFount = key
        years_and_graphs_map[minNotFount] = graph
    else:   # if we've already computed all the graphs
        minYear = min(years_and_weights_map.keys())
        for i in range(len(years_and_weights_map) - 1):
            years_and_graphs_map[minYear + i] = years_and_graphs_map[minYear + i + 1]
        years_and_graphs_map[minYear + len(years_and_weights_map) - 1] = graph

    # if we have all the graphs necessary to compute clusters
    if len(years_and_graphs_map) == len(years_and_weights_map):
        print 'Computing clusters for', (year - max(years_and_weights_map.keys()))
        clusters, percentNotInClusters = compute_clusters(years_and_weights_map, years_and_graphs_map, year - max(years_and_weights_map.keys()))

        years.append(year - max(years_and_weights_map.keys()))
        percentsNotInClusters.append(percentNotInClusters)

        print '  computing modularity'
        my_modularity_list.append(get_modularity_metric(years_and_graphs_map[0], clusters))

        # print '  computing term similarity'
        # term_metric_list.append(get_human_term_metric(clusters, nid_to_aid_map, conn))

        if CmtyV_t_minus_1 is not None:
            print '  computing temporal smoothness'
            temp_smoothness_list.append(get_temporal_smoothness_metric(CmtyV_t_minus_1, clusters))
        CmtyV_t_minus_1 = clusters

        num_clusters.append(clusters.Len())

        folder = 'output/dbscan/' + str(start_year) + '-' + str(end_year) + '/'

        np.savetxt(folder + 'years.txt', years, delimiter=',')
        np.savetxt(folder + 'my_modularity_list.txt', my_modularity_list, delimiter=',')
        # np.savetxt(folder + 'term_metric_list.txt', term_metric_list, delimiter=',')
        np.savetxt(folder + 'temp_smoothness_list.txt', temp_smoothness_list, delimiter=',')
        np.savetxt(folder + 'num_clusters.txt', num_clusters, delimiter=',')
        np.savetxt(folder + 'percentsNotInClusters.txt', percentsNotInClusters, delimiter=',')

close_db_conn(conn)