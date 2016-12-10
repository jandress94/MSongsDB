import snap
from db_utils import get_artist_terms
import random

def load_artist_terms(nid, nid_to_terms_map, nid_to_aid_map, conn):
    artist_term_tuples = get_artist_terms(nid_to_aid_map[nid], conn)
    nid_to_terms_map[nid] = set([term_tup[0] for term_tup in artist_term_tuples])

def get_communities_term_sim(comm1, comm2, nid_to_terms_map, nid_to_aid_map, sample_cutoff, conn):
    term_sim = 0
    pair_count = 0
    for nid1 in comm1:
        for nid2 in comm2:
            if nid1 == nid2 or (sample_cutoff < 1 and random.random() >= sample_cutoff): continue

            if nid1 not in nid_to_terms_map:
                load_artist_terms(nid1, nid_to_terms_map, nid_to_aid_map, conn)
            if nid2 not in nid_to_terms_map:
                load_artist_terms(nid2, nid_to_terms_map, nid_to_aid_map, conn)

            term_sim += 1.0 * len(nid_to_terms_map[nid1] & nid_to_terms_map[nid2]) / len(nid_to_terms_map[nid1] | nid_to_terms_map[nid2])
            pair_count += 1
    return term_sim, pair_count

# computes the human tag metric score for a provided community partitioning
# expects the first input to be of type snap.TCnComV
# also needs a map from node_id to artist_id
# returns "average similarity of all pairs which are in the same cluster", "average similarity of all pairs which are in different clusters"
def get_human_term_metric(communities, nid_to_aid_map, conn, sample_size = 3000):
    num_same_comm_pairs = 0
    num_diff_comm_pairs = 0
    same_comm_sim = 0
    diff_comm_sim = 0

    # get the terms for each node
    num_nodes = 0
    nid_to_terms_map = {}
    for comm in communities:
        for nid in comm:
            num_nodes += 1

    for commId1 in range(len(communities)):
        for commId2 in range(commId1 + 1):
            term_sim, pair_count = get_communities_term_sim(communities[commId1].NIdV, communities[commId2].NIdV, nid_to_terms_map, 
                                                            nid_to_aid_map, min(1.0, (1.0 * sample_size / num_nodes)**2), conn)
            if commId1 == commId2:
                same_comm_sim += term_sim
                num_same_comm_pairs += pair_count
            else:
                diff_comm_sim += term_sim
                num_diff_comm_pairs += pair_count
    if num_same_comm_pairs == 0:
        num_same_comm_pairs = 1
    if num_diff_comm_pairs == 0:
        num_diff_comm_pairs = 1
    return same_comm_sim / num_same_comm_pairs, diff_comm_sim / num_diff_comm_pairs

# computes the modularity of a provided community partitioning
# expects the first input to be of type snap.TCnComV
# returns the total modularity of the network
def get_modularity_metric(graph, communities):
    total_modularity = 0
    for community in communities:
        total_modularity += snap.GetModularity(graph, community.NIdV)
    return total_modularity

# computes the temporal smoothness counts across two years' community partitions
# expects the two inputs to be of type snap.TCnComV
# returns "number of pairs in the same state in t1 and t2", "number of pairs in different states in t1 and t2"
def get_temporal_smoothness_metric(comms_t1, comms_t2):
    # get the mapping from nid to community id in times t1 and t2
    nid_to_comm_map_t1 = {}
    for comm_t1_idx in range(len(comms_t1)):
        for n_t1 in comms_t1[comm_t1_idx]:
            nid_to_comm_map_t1[n_t1] = comm_t1_idx
    nid_to_comm_map_t2 = {}
    for comm_t2_idx in range(len(comms_t2)):
        for n_t2 in comms_t2[comm_t2_idx]:
            nid_to_comm_map_t2[n_t2] = comm_t2_idx

    same_state_pairs = 0
    diff_state_pairs = 0
    for nid1 in nid_to_comm_map_t1:
        if nid1 not in nid_to_comm_map_t2: continue
        for nid2 in nid_to_comm_map_t1:
            if nid2 not in nid_to_comm_map_t2: continue
            if nid1 == nid2: continue

            if (nid_to_comm_map_t1[nid1] == nid_to_comm_map_t1[nid2]) == (nid_to_comm_map_t2[nid1] == nid_to_comm_map_t2[nid2]):
                same_state_pairs += 1
            else:
                diff_state_pairs += 1
    return same_state_pairs, diff_state_pairs


