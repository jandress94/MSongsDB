from scipy import stats
import matplotlib.pyplot as plt
import numpy as np

def get_stat_signif(metric_algo1, metric_algo2, metric_results):
    stat, pval = stats.wilcoxon(metric_results[metric_algo1[0]][metric_algo1[1]], metric_results[metric_algo2[0]][metric_algo2[1]])
    print metric_algo1, metric_algo2, stat, pval

metrics_to_filename = {'Modularity': 'my_modularity_list.txt', 'Number of Clusters': 'num_clusters.txt', 
                        'Rand Index': 'temp_smoothness_list.txt', 'Term Similarity Ratio': 'term_metric_list.txt'}
algorithms = ['CNM', 'DBSCAN', 'FacetNet']
metric_results = {}

for metric in metrics_to_filename:
    metric_results[metric] = {}
    for algo in algorithms:
        filename = 'output/' + algo.lower() + '/1930-2010/' + ('alpha=0.5/' if algo == 'FacetNet' else '') + metrics_to_filename[metric]
        # print filename

        data = np.loadtxt(filename, delimiter=',')
        if metric == 'Rand Index':
            result_list = []
            for i in range(len(data)):
                result_list.append(data[i, 0] / (data[i, 0] + data[i, 1]))
            metric_results[metric][algo] = result_list
        elif metric == 'Term Similarity Ratio':
            result_list = []
            for i in range(len(data)):
                result_list.append(data[i, 0] / data[i, 1])
            metric_results[metric][algo] = result_list
        else:
            metric_results[metric][algo] = data.tolist()

for metric in metrics_to_filename:
    get_stat_signif((metric, 'CNM'), (metric, 'DBSCAN'), metric_results)
    get_stat_signif((metric, 'CNM'), (metric, 'FacetNet'), metric_results)

# years = np.loadtxt('output/cnm/1930-2010/years.txt', dtype = 'int', delimiter=',').tolist()

# counter = 0
# for metric in metrics_to_filename:
#     counter += 1
#     year_range = years if metric != 'Rand Index' else years[1:]

#     plt.figure(counter)
#     for algo in algorithms:
#         plt.plot(year_range, metric_results[metric][algo], label = algo)

#     plt.legend(loc='best')
#     plt.xlabel('Year')
#     plt.ylabel(metric)
#     plt.show()
    # plt.savefig('output/images/' + metric)



# metrics_to_filename = {'Modularity': 'my_modularity_list.txt', 'Number of Clusters': 'num_clusters.txt', 
#                         'Rand Index': 'temp_smoothness_list.txt', 'Term Similarity Ratio': 'term_metric_list.txt'}
# algorithms = ['FacetNet/1930-2010/alpha=0.2', 'FacetNet/1930-2010/alpha=0.5', 'FacetNet/1930-2010/alpha=0.8']
# metric_results = {}

# for metric in metrics_to_filename:
#     metric_results[metric] = {}
#     for algo in algorithms:
#         filename = 'output/' + algo.lower() + '/' + metrics_to_filename[metric]
#         print filename

#         data = np.loadtxt(filename, delimiter=',')
#         if metric == 'Rand Index':
#             result_list = []
#             for i in range(len(data)):
#                 result_list.append(data[i, 0] / (data[i, 0] + data[i, 1]))
#             metric_results[metric][algo] = result_list
#         elif metric == 'Term Similarity Ratio':
#             result_list = []
#             for i in range(len(data)):
#                 result_list.append(data[i, 0] / data[i, 1])
#             metric_results[metric][algo] = result_list
#         else:
#             metric_results[metric][algo] = data.tolist()

years = np.loadtxt('output/cnm/1930-2010/years.txt', dtype = 'int', delimiter=',').tolist()

# counter = 0
# for metric in metrics_to_filename:
#     counter += 1
#     year_range = years if metric != 'Rand Index' else years[1:]

#     plt.figure(counter)
#     for algo in algorithms:
#         plt.plot(year_range, metric_results[metric][algo], label = algo)

#     plt.legend(loc='best')
#     plt.xlabel('Year')
#     plt.ylabel(metric)
#     plt.show()

data = np.loadtxt('output/cnm/1930-2010/nodes_and_edges.txt', delimiter=',')
result_list = [elem[0] for elem in data.tolist()]
print result_list
plt.figure(1)
plt.plot(years, result_list)

plt.legend(loc='best')
plt.xlabel('Year')
plt.ylabel('Number of Nodes')
plt.show()