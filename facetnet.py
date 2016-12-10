from db_utils import *
from graph_utils import *
from facetnet_utils import *
import snap
import numpy as np 

db_filename = 'D:/artist_full.db'

conn = open_db_conn(db_filename)

artist_list = get_artists(conn)

artist_id_to_int = {}
nid_to_aid_map = {}

for i in xrange(len(artist_list)):
    artist_id_to_int[artist_list[i][0]] = i + 1 
    nid_to_aid_map[i + 1] = artist_list[i][0]

start_year = 1930
end_year = 2010
alpha = 0.5

year_range = range(start_year - 1, end_year + 1)
year_prev = False
cluster_size_range = range(6, 16)

for year in year_range:
    print 'Building graph for', year
    graph = build_graph(conn, year, artist_id_to_int)

    W, X, L, all_vertex_ids, nid_to_index_map = initialize(graph, num_clusters)
    num_iter = 0
    if year_prev:
    	X_prev = add_and_remove_nodes(X_prev, all_vertex_ids_prev, nid_to_index_map_prev, all_vertex_ids)
    	X_next, L_next = update(W, X, L, X_prev, L_prev, alpha)


    year_prev = True