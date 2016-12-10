from db_utils import *
from graph_utils import *
from metrics import *
import snap
import time
import numpy as np 

db_filename = 'D:/artist_full.db'

conn = open_db_conn(db_filename)

artist_id_to_int, nid_to_aid_map = get_id_mapping(conn)

years = []
nodes_and_edges = []
snap_modularity_list = []
my_modularity_list = []
term_metric_list = []
temp_smoothness_list = []
num_clusters = []

CmtyV_t_minus_1 = None

for year in range(1930, 2011):
    print year
    years.append(year)

    print '  building graph'
    graph = build_graph(conn, year, artist_id_to_int)
    nodes_and_edges.append((graph.GetNodes(), graph.GetEdges()))
    CmtyV = snap.TCnComV()

    print '  computing communities'
    snap_modularity = snap.CommunityCNM(graph, CmtyV)
    snap_modularity_list.append(snap_modularity)

    print '  computing modularity'
    my_modularity_list.append(get_modularity_metric(graph, CmtyV))

    print '  computing term similarity'
    term_metric_list.append(get_human_term_metric(CmtyV, nid_to_aid_map, conn))

    if CmtyV_t_minus_1 is not None:
        print '  computing temporal smoothness'
        temp_smoothness_list.append(get_temporal_smoothness_metric(CmtyV_t_minus_1, CmtyV))
    CmtyV_t_minus_1 = CmtyV

    num_clusters.append(CmtyV.Len())

    np.savetxt('years.txt', years, delimiter=',')
    np.savetxt('nodes_and_edges.txt', nodes_and_edges, delimiter=',')
    np.savetxt('snap_modularity_list.txt', snap_modularity_list, delimiter=',')
    np.savetxt('my_modularity_list.txt', my_modularity_list, delimiter=',')
    np.savetxt('term_metric_list.txt', term_metric_list, delimiter=',')
    np.savetxt('temp_smoothness_list.txt', temp_smoothness_list, delimiter=',')
    np.savetxt('num_clusters.txt', num_clusters, delimiter=',')

close_db_conn(conn)