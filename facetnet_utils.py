from db_utils import *
from graph_utils import *
import snap
import numpy as np 
from sklearn.preprocessing import normalize
import timeit

def KL_divergence(A, B):
	(m, n) = A.shape
	div = 0
	for i in xrange(m):
		for j in xrange(n):
			if A[i, j] > 0 and B[i, j] > 0:
				div += A[i, j]*(np.log(float(A[i, j]) / B[i, j]) - 1) + B[i, j]
	return div
# L = Lambda matrix
def get_cost(W, X, L, Z, alpha):
	Y = np.dot(X, L)
	#Y_prev = np.dot(X_prev, L_prev)
	XLXT = np.dot(Y, np.transpose(X))
	#XLXT_prev = np.dot(Y_prev, np.transpose(X_prev))
	CS = KL_divergence(W, XLXT)
	CT = KL_divergence(Z, XLXT)
	return alpha*CS + (1-alpha)*CT

def D_inverse(Y):
	(n, m) = Y.shape
	D_inv = np.zeros((n, n))
	#Y = np.dot(X, L)
	for i in xrange(n):
		D_inv[i, i] = 1.0 / np.sum(Y[i, :])
	return D_inv

def soft_modularity(W, X, L):
	(n, m) = X.shape
	Y = np.dot(X, L)
	D_inv = D_inverse(Y)
	M = np.dot(D_inv, Y)
	# assume W = W^T
	N = np.dot(np.ones((1, n)), np.dot(W, M))
	Q_s = np.trace(np.dot(np.transpose(M), np.dot(W, M))) - np.dot(N, np.transpose(N))
	return Q_s[0][0]

def initialize(graph):
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

	return W, all_vertex_ids, nid_to_index_map

def initialize_XL(n, num_clusters):
	#X = (1.0 / n) * np.ones((n, num_clusters))
	#np.random.seed(42)
	X = np.random.rand(n, num_clusters)
	X = normalize(X, axis = 0, norm = 'l1')

	L = np.diag([1.0/num_clusters for _ in xrange(num_clusters)])
	return X, L

def add_and_remove_nodes(Z_prev, all_vertex_ids_prev, nid_to_index_map_prev, all_vertex_ids):
	n = len(all_vertex_ids)
	Z_prev_adjusted = np.zeros((n, n))
	for i in xrange(n):
		for j in xrange(n):
			node_i = all_vertex_ids[i]
			node_j = all_vertex_ids[j]
			if (node_i in all_vertex_ids_prev) and (node_j in all_vertex_ids_prev):
				Z_prev_adjusted[i, j] = Z_prev[nid_to_index_map_prev[node_i], nid_to_index_map_prev[node_j]]
	Z_prev_adjusted = 1.0/np.sum(np.sum(Z_prev_adjusted)) * Z_prev_adjusted
	return Z_prev_adjusted


def update(W, X, L, Z, alpha):
	XLXT = np.dot(X, np.dot(L, np.transpose(X)))
	#Z = np.dot(X_prev, np.dot(L_prev, np.transpose(X_prev)))

	X_next = np.zeros(X.shape)
	L_next = np.zeros(L.shape)
	(n, m) = X.shape
	for k in xrange(m):
		sum_i = np.zeros(n)
		for i in xrange(n):
			with np.errstate(divide='ignore', invalid='ignore'):
				v = np.divide(alpha*W[i, :] + (1 - alpha)*Z[i, :], XLXT[i, :])
				v[XLXT[i, :] == 0] = 0
			sum_j = np.dot(v, X[:, k])
			'''
			sum_j = 0
			for j in xrange(n):
				elem = XLXT[i, j]
				if elem != 0:
					sum_j += (alpha*W[i, j] + (1 - alpha)*Z[i, j]) * X[j, k] / elem
			'''
			sum_i[i] = sum_j
			X_next[i, k] = X[i, k] * sum_j * L[k, k]
		L_next[k, k] = np.dot(sum_i, X[:, k])
		L_next[k, k] *= L[k, k]
	X_next = normalize(X_next, axis = 0, norm = 'l1')
	L_next = normalize(np.diag(L_next).reshape(1, -1), norm = 'l1')
	L_next = np.diag(L_next[0])
	return X_next, L_next

def compute_clusters(X, L, all_vertex_ids):
	(n, m) = X.shape
	Y = np.dot(X, L)
	D_inv = D_inverse(Y)
	member = np.dot(D_inv, Y)
	communities = [snap.TIntV() for _ in xrange(m)]
	for node in xrange(n):
		comm = np.argmax(member[node, :])
		communities[comm].Add(all_vertex_ids[node])
	# potentially remove empty communities
	clusters = snap.TCnComV()
	for cluster in communities:
		if not cluster.Empty():
			clusters.Add(snap.TCnCom(cluster))
	return clusters

