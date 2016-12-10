from db_utils import *
from graph_utils import *
import snap
import numpy as np 
from sklearn.preprocessing import normalize

def KL_divergence(A, B):
	(m, n) = A.shape
	div = 0
	for i in xrange(m):
		for j in xrange(n):
			if A[i, j] > 0 and B[i, j] > 0:
				div += A[i, j]*(np.log(float(A[i, j]) / B[i, j]) - 1) + B[i, j]
	return div
# L = Lambda matrix
def cost(W, X, L, X_prev, L_prev, alpha):
	Y = np.dot(X, L)
	Y_prev = np.dot(X_prev, L_prev)
	XLXT = np.dot(Y, np.transpose(X))
	XLXT_prev = np.dot(Y_prev, np.transpose(X_prev))
	CS = KL_divergence(W, XLXT)
	CT = KL_divergence(XLXT_prev, XLXT)
	return alpha*CS + (1-alpha)*CT

def D_inverse(X, L):
	(n, m) = X.shape
	D_inv = np.zeros((n, n))
	Y = np.dot(X, L)
	for i in xrange(n):
		D_inv[i, i] = 1.0 / np.sum(Y[i, :])

def soft_modularity(W, X, L):
	(n, m) = X.shape
	D_inv = D_inverse(X, L)
	M = np.dot(D_inv, np.dot(X, L))
	# assume W = W^T
	N = np.dot(np.ones((1, n)), np.dot(W, M))
	Q_s = np.trace(np.dot(np.transpose(M), np.dot(W, M))) - np.dot(N, np.transpose(N))
	return Q_s

def initialize(graph, num_clusters):
	n = graph.GetNodes()
	num_edges = graph.GetEdges()

	all_vertex_ids = []
	nid_to_index_map = {}

	for node in graph.Nodes():
		all_vertex_ids.append(node.GetId())

	all_vertex_ids = np.sort(all_vertex_ids)

	W = np.zeros((n, n))
	for i in xrange(n):
		node_i = all_vertex_ids[i]
		nid_to_index_map[node_i] = i
		for j in xrange(n):
			node_j = all_vertex_ids[j]
			if graph.IsEdge(node_i, node_j):
				W[i, j] = 1.0 / (2 * num_edges)

	X = (1.0 / n) * np.zeros((n, n))

	L = np.diag([1.0/num_clusters for _ in xrange(num_clusters)])

	return W, X, L, all_vertex_ids, nid_to_index_map

def add_and_remove_nodes(X_prev, all_vertex_ids_prev, nid_to_index_map_prev, all_vertex_ids):
	n = len(all_vertex_ids)
	X_prev_adjusted = np.zeros((n, n))
	for i in xrange(n):
		node = all_vertex_ids[i]
		if node in all_vertex_ids_prev:
			X_prev_adjusted[i, :] = X_prev[nid_to_index_map_prev[node], :]
	return X_prev_adjusted


def update(W, X, L, X_prev, L_prev, alpha):
	XLXT = np.dot(X, np.dot(L, np.transpose(X)))
	Z = np.dot(X_prev, np.dot(L_prev, np.transpose(X_prev)))

	X_next = np.zeros(X.shape)
	L_next = np.zeros(L.shape)
	(n, m) = X.shape

	for k in xrange(m):
		for i in xrange(n):
			sum_j = 0
			for j in xrange(n):
				if XLXT[i, j] != 0:
					sum_j += (alpha*W[i, j] + (1 - alpha)*Z[i, j]) * X[j, k] / XLXT[i, j]
			X_next[i, k] = X[i, k] * L[k, k] * sum_j
			L_next[k, k] += X[i, k] * sum_j
		L_next[k, k] *= L[k, k]

	X_next = normalize(X_next, axis = 0, norm = 'l1')
	L_next = normalize(np.diag(L_next).reshape(1, -1), norm = 'l1')
	L_next = np.diag(L_next[0])
	return X_next, L_next

def compute_clusters(X, L, all_vertex_ids):
	(n, m) = X.shape
	D_inv = D_inverse(X, L)
	Y = np.dot(X, L)
	member = np.dot(D_inv, Y)
	communities = [snap.TIntV() for _ in xrange(m)]
	for node in xrange(n):
		comm = np.argmax(member[i, :])
		communities[comm].Add(all_vertex_ids[node])
	# potentially remove empty communities
	clusters = snap.TCnComV()
	for cluster in communities:
		if not cluster.Empty():
			clusters.Add(snap.TCnCom(cluster))
	return communities

D = np.array([[1.0, 2], [2.0, 3]])
print normalize(D, axis = 0, norm = 'l1')
D = normalize(np.diag(D).reshape(1, -1), norm = 'l1')
print np.diag(D[0])
a = [1, 2, 4, -1]
print np.sort(a)
