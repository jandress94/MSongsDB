from db_utils import *
from graph_utils import *
import snap
import time
import numpy as np 

db_filename = 'D:/artist_full.db'

conn = open_db_conn(db_filename)

artist_list = get_artists(conn)

artist_id_to_int = {}

for i in xrange(len(artist_list)):
	artist_id_to_int[artist_list[i][0]] = i + 1

f = open('input/id_mapping.txt', 'w')
for key in artist_id_to_int:
    f.write(str(key) + ',' + str(artist_id_to_int[key]) + '\n')
f.close

for year in range(1930, 2011):
    print year
    graph = build_graph(conn, year, artist_id_to_int)
    snap.SaveEdgeList(graph, 'input/' + str(year) + '_edges.txt')

close_db_conn(conn)