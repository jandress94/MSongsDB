from db_utils import *
from graph_utils import *
import snap
import time
import numpy as np 

db_filename = 'D:/artist_full.db'

conn = open_db_conn(db_filename)

# print 'creating indices'
# create_sim_artist_indices(conn)
# print 'done'

artist_list = get_artists(conn)

artist_id_to_int = {}

for i in xrange(len(artist_list)):
	artist_id_to_int[artist_list[i][0]] = i + 1 


years = []
nodes_and_edges = []
modularity_list = []
num_clusters = []

for year in range(1930, 2011):
	print year
	years.append(year)
	graph = build_graph(conn, year, artist_id_to_int)
	nodes_and_edges.append((graph.GetNodes(), graph.GetEdges()))
	CmtyV = snap.TCnComV()
	modularity = snap.CommunityCNM(graph, CmtyV)
	modularity_list.append(modularity)
	num_clusters.append(CmtyV.Len())

np.savetxt('years.txt', years, delimiter=',')
np.savetxt('nodes_and_edges.txt', nodes_and_edges, delimiter=',')
np.savetxt('modularity_list.txt', modularity_list, delimiter=',')
np.savetxt('num_clusters.txt', num_clusters, delimiter=',')