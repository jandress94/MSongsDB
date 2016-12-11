from db_utils import *
from graph_utils import *

db_filename = 'D:/artist_full.db'
conn = open_db_conn(db_filename)
artist_id_to_int, nid_to_aid_map = get_id_mapping(conn)

f = open('input/cluster_ids.txt')
for line in f:
    node_id = int(line)
    artist_id = nid_to_aid_map[node_id]
    print node_id, get_artist_name(artist_id, conn)

close_db_conn(conn)