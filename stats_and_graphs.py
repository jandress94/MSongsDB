from scipy import stats
import matplotlib.pyplot as plt
import numpy as np

metrics_to_filename = {'Modularity': 'my_modularity_list.txt', 'Number of Clusters': 'num_clusters.txt', 
                        'Rand Index': 'temp_smoothness_list.txt', 'Term Similarity Ratio': 'term_metric_list.txt'}
algorithms = ['CNM', 'DBSCAN']#, 'FacetNet']
metric_results = {}

for metric in metrics_to_filename:
    metric_results[metric] = {}
    for algo in algorithms:
        filename = 'output/' + algo.lower() + '/1930-2010/' + ('alpha=0.5/' if algo == 'FacetNet' else '') + metrics_to_filename[metric]
        print filename

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

years = np.loadtxt('output/cnm/1930-2010/years.txt', dtype = 'int', delimiter=',').tolist()

counter = 0
for metric in metrics_to_filename:
    counter += 1
    year_range = years if metric != 'Rand Index' else years[1:]

    plt.figure(counter)
    for algo in algorithms:
        plt.plot(year_range, metric_results[metric][algo], label = algo)

    plt.legend()
    plt.xlabel('Year')
    plt.ylabel(metric)
    plt.show()
    # plt.savefig('output/images/' + metric)

# stats.wilcoxon(x, y)