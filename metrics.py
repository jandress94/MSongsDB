import snap
from db_utils import get_artist_terms

def get_communities_term_sim(comm1, comm2, nid_to_terms_map):
    term_sim = 0
    for nid1 in comm1:
        for nid2 in comm2:
            if nid1 == nid2: continue
            term_sim += 1.0 * len(nid_to_terms_map[nid1] & nid_to_terms_map[nid2]) / len(nid_to_terms_map[nid1] | nid_to_terms_map[nid2])
    return term_sim

# computes the human tag metric score for a provided community partitioning
# expects the first input to be of type snap.TCnComV
# also needs a map from node_id to artist_id
# returns "average similarity of all pairs which are in the same cluster", "average similarity of all paris which are in different clusters"
def get_human_term_metric(communities, nid_to_aid_map, conn):
    num_same_comm_pairs = 0
    num_diff_comm_pairs = 0
    same_comm_sim = 0
    diff_comm_sim = 0

    # get the terms for each node
    nid_to_terms_map = {}
    for comm in communities:
        for nid in comm:
            artist_term_tuples = get_artist_terms(nid_to_aid_map[nid], conn)
            nid_to_terms_map[nid] = set([term_tup[0] for term_tup in artist_term_tuples])

    for commId1 in range(len(communities)):
        for commId2 in range(commId1 + 1):
            term_sim = get_communities_term_sim(communities[commId1].NIdV, communities[commId2].NIdV, nid_to_terms_map)
            if commId1 == commId2:
                same_comm_sim += term_sim / 2
                num_same_comm_pairs += len(communities[commId1]) * (len(communities[commId1]) - 1) / 2
            else:
                diff_comm_sim += term_sim
                num_diff_comm_pairs += len(communities[commId1]) * len(communities[commId2])
    return same_comm_sim / num_same_comm_pairs, diff_comm_sim / num_diff_comm_pairs

# computes the modularity of a provided community partitioning
# expects the first input to be of type snap.TCnComV
# returns the total modularity of the network
def get_modularity_metric(graph, communities):
    total_modularity = 0
    for community in communities:
        total_modularity += snap.GetModularity(graph, community.NIdV)
    return total_modularity