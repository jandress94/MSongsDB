from db_utils import *
from graph_utils import *
from scipy import sparse
import random
import math
import snap
from sklearn.cluster import DBSCAN

db_filename = 'D:/artist_full.db'

conn = open_db_conn(db_filename)

artist_list = get_artists(conn)

artist_id_to_int = {}
nid_to_aid_map = {}

for i in xrange(len(artist_list)):
    artist_id_to_int[artist_list[i][0]] = i + 1 
    nid_to_aid_map[i + 1] = artist_list[i][0]

print 'Building graph...'
graph = build_graph(conn, 1965, artist_id_to_int)

dists = sparse.lil_matrix((graph.GetNodes(), graph.GetNodes()))
nodeIds = []
for node in graph.Nodes():
    nodeIds.append(node.GetId())

zero_dist = 0
non_zero_dist = 0

print 'Computing distances'
for i in xrange(len(nodeIds)):
    node1 = graph.GetNI(nodeIds[i])
    for j in xrange(i):

        if not graph.IsEdge(node1.GetId(), nodeIds[j]): continue

        sameNeighborCount = 0
        for neighbor in node1.GetOutEdges():
            if graph.IsEdge(nodeIds[j], neighbor):
                sameNeighborCount += 1

        if sameNeighborCount != 0:
            dist = 1.0 - (1.0 * sameNeighborCount / math.sqrt(node1.GetDeg() * graph.GetNI(nodeIds[j]).GetDeg()))
            dists[i,j] = dist
            dists[j,i] = dist

print 'Computing clusters'
# db = DBSCAN(metric='precomputed').fit(dists)
db = DBSCAN(metric='precomputed').fit(dists.tocsr())

labels = db.labels_

n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
print 'got', n_clusters, 'clusters'

close_db_conn(conn)