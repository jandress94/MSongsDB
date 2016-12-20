from db_utils import *
from graph_utils import *
from facetnet_utils import *
from metrics import *
import snap
import numpy as np 
import timeit

db_filename = 'D:/artist_full.db'

conn = open_db_conn(db_filename)

artist_list = get_artists(conn)

artist_id_to_int, nid_to_aid_map = get_id_mapping(conn)

start_year = 1930
end_year = 1950
alpha = 0.2
num_iter = 20

year_range = range(start_year - 1, end_year + 1)

years = []
my_modularity_list = []
term_metric_list = []
temp_smoothness_list = []
num_clusters_list = []

clusters_prev = None
window_half_size = 2
min_num_clusters = 3
max_num_clusters = 15
num_clusters_prev = min_num_clusters + window_half_size
#cluster_size_range = range(min_num_clusters, max_num_clusters+1)

for year in year_range:
    print 'Building graph for', year
    years.append(year)
    graph = build_graph(conn, year, artist_id_to_int)

    if graph.GetNodes() == 0:
    	print 'Hit the end'
    	break

    # map num_clusters to modularity
    num_clusters_to_modularity = {}
    cluster_size_range = range(min(max(num_clusters_prev - window_half_size, min_num_clusters), max_num_clusters-2*window_half_size) , max(min(num_clusters_prev + window_half_size + 1, max_num_clusters + 1), min_num_clusters + 2*window_half_size+1))

    X_max = None
    L_max = None
    all_vertex_ids_max = None
    nid_to_index_map_max = None
    modularity_max = float("-inf")
    clusters_max = None
    num_clusters_max = None

    W, all_vertex_ids, nid_to_index_map = initialize(graph)
    if clusters_prev is not None:
    	Z_prev = add_and_remove_nodes(Z_prev, all_vertex_ids_prev, nid_to_index_map_prev, all_vertex_ids)

    for num_clusters in cluster_size_range:
		print num_clusters
		X, L = initialize_XL(graph.GetNodes(), num_clusters)
		
		for i in xrange(num_iter):
			#print "Update number " + str(i+1)
			if clusters_prev is not None:
				X, L = update(W, X, L, Z_prev, alpha)
			else:
				Z = np.zeros(W.shape)
				X, L = update(W, X, L, Z, 1.0)


			'''
			if year_prev:
				#X_prev = add_and_remove_nodes(X_prev, all_vertex_ids_prev, nid_to_index_map_prev, all_vertex_ids, num_clusters)
				#if num_iter == 1:
				#Z_prev = add_and_remove_nodes(Z_prev, all_vertex_ids_prev, nid_to_index_map_prev, all_vertex_ids)
				X_next, L_next = update(W, X, L, Z_prev, alpha)
				if (num_iter % 10 == 0):
					cost_next = get_cost(W, X_next, L_next, Z_prev, alpha)
					cost = get_cost(W, X, L, Z_prev, alpha)
			else:
				Z = np.zeros(W.shape)
				X_next, L_next = update(W, X, L, Z, 1.0)
				Z_next = np.dot(X_next, np.dot(L_next, np.transpose(X_next)))
				if (num_iter % 10 == 0):
					cost_next = get_cost(W, X_next, L_next, Z_next, 1.0)
					cost = get_cost(W, X, L, Z, 1.0)

			X = X_next
			L = L_next

			if (num_iter % 10 == 0): #abs(cost - cost_next) < 0.01*cost:
				if abs(cost - cost_next) < 0.02*cost:
					break
			'''
		Q = soft_modularity(W, X, L)
		num_clusters_to_modularity[num_clusters] = Q
		if Q > modularity_max:
				X_max = X
				L_max = L
				all_vertex_ids_max = all_vertex_ids
				nid_to_index_map_max = nid_to_index_map
				modularity_max = Q
				clusters_max = compute_clusters(X, L, all_vertex_ids)
				num_clusters_max = num_clusters

    Z_prev = np.dot(X_max, np.dot(L_max, np.transpose(X_max)))
    all_vertex_ids_prev = all_vertex_ids_max
    nid_to_index_map_prev = nid_to_index_map_max

    print "The maximum modularity is achieved with " + str(num_clusters_max) + " clusters"
    print num_clusters_to_modularity

    num_clusters_list.append(num_clusters_max)

    print '  computing modularity'
    my_modularity_list.append(get_modularity_metric(graph, clusters_max))

    print '  computing term similarity'
    term_metric_list.append(get_human_term_metric(clusters_max, nid_to_aid_map, conn))

    if clusters_prev:
		print '  computing temporal smoothness'
		temp_smoothness_list.append(get_temporal_smoothness_metric(clusters_prev, clusters_max))
    num_clusters_prev = num_clusters_max
    clusters_prev = clusters_max

    folder = 'output/facetnet/' + str(start_year) + '-' + str(end_year) + '/' + 'alpha=' + str(alpha) + '/'

    np.savetxt(folder + 'years.txt', years, delimiter=',')
    np.savetxt(folder + 'my_modularity_list.txt', my_modularity_list, delimiter=',')
    np.savetxt(folder + 'term_metric_list.txt', term_metric_list, delimiter=',')
    np.savetxt(folder + 'temp_smoothness_list.txt', temp_smoothness_list, delimiter=',')
    np.savetxt(folder + 'num_clusters.txt', num_clusters_list, delimiter=',')

close_db_conn(conn)