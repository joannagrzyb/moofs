import os
import numpy as np

from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC

from sklearn.feature_selection import chi2

from utils import find_datasets, load_feature_costs
from methods.fsclf import FeatueSelectionClf
from methods.gaaccclf import GeneticAlgorithmAccuracyClf
from methods.gaacccost import GAAccCost
from methods.nsgaacccost import NSGAAccCost

import matplotlib.pyplot as plt

DATASETS_DIR = os.path.join(os.path.realpath(os.path.dirname(__file__)), 'datasets')
n_datasets = len(list(enumerate(find_datasets(DATASETS_DIR))))

# !!! Change before run !!!
base_classifiers = {
    'GNB': GaussianNB(),
    'SVM': SVC(),
    'kNN': KNeighborsClassifier(),
    'CART': DecisionTreeClassifier(random_state=10),
}

# !!! Change before run !!!
methods_alias = [
                "FS",
                "GA_a",
                "GA_ac",
                "NSGA_a",
                "NSGA_c",
                "NSGA_p"
]

test_size = 0.2
n_folds = 10
n_methods = len(methods_alias) * len(base_classifiers)
mean_scores = np.zeros((n_datasets, 21, n_methods))
stds = np.zeros((n_datasets, 21, n_methods))
mean_costs = np.zeros((n_datasets, 21, n_methods))
datasets = []
base_clf_alias = []
n_base_clfs = len(base_classifiers)
# Pareto decision for NSGA
pareto_decision_a = 'accuracy'
pareto_decision_c = 'cost'
pareto_decision_p = 'promethee'
n_rows_p = 50

# Load data from file
for dataset_id, dataset in enumerate(find_datasets(DATASETS_DIR)):
    datasets.append(dataset)
    feature_number = len(load_feature_costs(dataset))
    scale_features = np.linspace(1/feature_number, 1.0, feature_number)
    scale_features += 0.01
    for scale_id, scale in enumerate(scale_features):
        selected_feature_number = int(scale * feature_number)
        methods = {}
        for key, base in base_classifiers.items():
            base_clf_alias.append(key)

            # !!! Change before run !!!
            methods['FS_{}'.format(key)] = FeatueSelectionClf(base, chi2, scale)
            methods['GAacc_{}'.format(key)] = GeneticAlgorithmAccuracyClf(base, scale, test_size)
            methods['GAaccCost_{}'.format(key)] = GAAccCost(base, scale, test_size)
            methods['NSGAaccCost_acc_{}'.format(key)] = NSGAAccCost(base, scale, test_size, pareto_decision_a)
            methods['NSGAaccCost_cost_{}'.format(key)] = NSGAAccCost(base, scale, test_size, pareto_decision_c)
            methods['NSGAaccCost_promethee_{}'.format(key)] = NSGAAccCost(base, scale, test_size, pareto_decision_p)
        for clf_id, clf_name in enumerate(methods):
            try:
                filename_acc = "results/experiment1/accuracy/%s/f%d/%s.csv" % (dataset, selected_feature_number, clf_name)
                scores = np.genfromtxt(filename_acc, delimiter=',', dtype=np.float32)
                mean_score = np.mean(scores)
                mean_scores[dataset_id, scale_id, clf_id] = mean_score
                std = np.std(scores)
                stds[dataset_id, scale_id, clf_id] = std
                print("Accuracy: ", mean_score, std)

                filename_cost = "results/experiment1/cost/%s/f%d/%s.csv" % (dataset, selected_feature_number, clf_name)
                total_cost = np.genfromtxt(filename_cost, delimiter=',', dtype=np.float32)
                mean_cost = np.mean(total_cost)
                mean_costs[dataset_id, scale_id, clf_id] = mean_cost
                # print("Cost: ", mean_cost)
            except IOError:
                print("File", filename_acc, "not found")
                print("File", filename_cost, "not found")


# Bar charts
methods_labels = methods_alias * len(base_classifiers)
width = 1/(len(methods_alias)+1)
tr = 1/(len(methods_alias)/2)
for dataset_id, dataset in enumerate(find_datasets(DATASETS_DIR)):
    feature_number = len(load_feature_costs(dataset))
    scale_features = np.linspace(1/feature_number, 1.0, feature_number)
    scale_features += 0.01
    for key, base in base_classifiers.items():
        r = 0
        for clf_id, (clf_name, method_label) in enumerate(zip(methods, methods_labels)):
            if key in clf_name:
                plot_data = []
                for scale_id, scale in enumerate(scale_features):
                    selected_feature_number = int(scale * feature_number)
                    plot_data.append(mean_scores[dataset_id, scale_id, clf_id])
                position = list(range(1, len(plot_data)+1))
                # Add plot_data to bars in the chart
                plt.bar([p - tr + width*r for p in position], plot_data, width, edgecolor='white', label=method_label)
                r += 1
        # Save plot
        filename = "results/experiment1/plots/%s_%s_acc" % (dataset, key)
        if not os.path.exists("results/experiment1/plots/"):
            os.makedirs("results/experiment1/plots/")

        plt.ylabel("Accuracy")
        plt.xlabel("Number of selected features")
        plt.ylim(bottom=0.0, top=1.0)
        plt.title(f"Accuracy for dataset {dataset} and base classifier {key}")
        plt.legend(loc='best')
        plt.grid(True, color="silver", linestyle=":", axis='y')
        plt.xticks(range(1, len(plot_data)+1), labels=range(1, len(plot_data)+1))
        plt.gcf().set_size_inches(9, 6)
        plt.savefig(filename+".png", bbox_inches='tight')
        plt.savefig(filename+".eps", format='eps', bbox_inches='tight')
        plt.clf()
        plt.close()

    for key, base in base_classifiers.items():
        r = 0
        for clf_id, (clf_name, method_label) in enumerate(zip(methods, methods_labels)):
            if key in clf_name:
                plot_data = []
                for scale_id, scale in enumerate(scale_features):
                    selected_feature_number = int(scale * feature_number)
                    plot_data.append(mean_costs[dataset_id, scale_id, clf_id])
                position = list(range(1, len(plot_data)+1))
                # Add plot_data to bars in the chart
                plt.bar([p - tr + width*r for p in position], plot_data, width, edgecolor='white', label=method_label)
                r += 1
        # Save plot
        filename = "results/experiment1/plots/%s_%s_cost" % (dataset, key)
        if not os.path.exists("results/experiment1/plots/"):
            os.makedirs("results/experiment1/plots/")

        plt.ylabel("Cost")
        plt.xlabel("Number of selected features")
        plt.ylim(bottom=0.0)
        plt.title(f"Cost for dataset {dataset} and base classifier {key}")
        plt.legend(loc='best')
        plt.xticks(range(1, len(plot_data)+1), labels=range(1, len(plot_data)+1))
        plt.grid(True, color="silver", linestyle=":", axis='y')
        plt.gcf().set_size_inches(9, 6)
        plt.savefig(filename+".png", bbox_inches='tight')
        plt.savefig(filename+".eps", format='eps', bbox_inches='tight')
        plt.clf()
        plt.close()

# #############################################################################
# Plot pareto front scatter
# for dataset_id, dataset in enumerate(find_datasets(DATASETS_DIR)):
#     for scale_id, scale in enumerate(scale_features):
#         selected_feature_number = int(scale * feature_number)
#         for fold_id in range(n_folds):
#             solutions = []
#             for sol_id in range(n_rows_p):
#                 try:
#                     filename_pareto = "results/experiment1/pareto/%s/f%d/fold%d/sol%d.csv" % (dataset, selected_feature_number, fold_id, sol_id)
#                     solution = np.genfromtxt(filename_pareto, dtype=np.float32)
#                     solution = solution.tolist()
#                     solution[0] = solution[0] * (-1)
#                     solutions.append(solution)
#                 except IOError:
#                     pass
#             filename_pareto_chart = "results/experiment1/plot_scatter/%s/%s_f%d_fold%d_pareto" % (dataset, dataset, selected_feature_number, fold_id)
#             if not os.path.exists("results/experiment1/plot_scatter/%s/" % (dataset)):
#                 os.makedirs("results/experiment1/plot_scatter/%s/" % (dataset))
#             print(solutions)
#             x = []
#             y = []
#             for solution in solutions:
#                 x.append(solution[0])
#                 y.append(solution[1])
#             x = np.array(x)
#             y = np.array(y)
#             axes = plt.gca()
#             plt.scatter(x, y, color='black')
#             plt.title("Objective Space")
#             plt.xlabel('Accuracy')
#             plt.ylabel('Cost')
#             plt.grid(True, color="silver", linestyle=":", axis='both')
#             plt.gcf().set_size_inches(9, 6)
#             plt.savefig(filename_pareto_chart+".png", bbox_inches='tight')
#             plt.savefig(filename_pareto_chart+".eps", format='eps', bbox_inches='tight')
#             plt.clf()
#             plt.close()


# DON'T RUN
# #############################################################################
# Latex tables not working for this case
# n_features = []
# scale_features = []
# for dataset_id, dataset in enumerate(find_datasets(DATASETS_DIR)):
#     n_f = len(load_feature_costs(dataset))
#     n_features.append(n_f)
#     s_f = np.linspace(1/n_f, 1.0, n_f)
#     s_f += 0.01
#     scale_features.append(s_f)

# for key in base_classifiers:
#     for scale_id, scale in enumerate(scale_features[0]):
#         acc_contents = [[None for _ in range(len(methods_alias))] for _ in range(n_datasets)]
#         cost_contents = [[None for _ in range(len(methods_alias))] for _ in range(n_datasets)]
#         for dataset_id, dataset in enumerate(find_datasets(DATASETS_DIR)):
#             selected_feature_number = int(scale * n_features[dataset_id])
#             i = 0
#             if dataset_id == 0:
#                 for clf_id, clf_name in enumerate(methods):
#                     if key in clf_name:
#                         # Accuracy
#                         ms = mean_scores[dataset_id, scale_id, clf_id].tolist()
#                         std = stds[dataset_id, scale_id, clf_id].tolist()
#                         string = str(float("{:.2f}".format(ms))) + " +- " + str(float("{:.2f}".format(std)))
#                         acc_contents[dataset_id][i] = string
#
#                         # Cost
#                         mc = mean_costs[dataset_id, scale_id, clf_id].tolist()
#                         value = float("{:.2f}".format(mc))
#                         cost_contents[dataset_id][i] = value
#                         i += 1
#
#             if (dataset_id > 0) and (selected_feature_number <= n_features[dataset_id-1]):
#                 for clf_id, clf_name in enumerate(methods):
#                     if key in clf_name:
#                         # Accuracy
#                         ms = mean_scores[dataset_id, scale_id, clf_id].tolist()
#                         std = stds[dataset_id, scale_id, clf_id].tolist()
#                         string = str(float("{:.2f}".format(ms))) + " +- " + str(float("{:.2f}".format(std)))
#                         acc_contents[dataset_id][i] = string
#
#                         # Cost
#                         mc = mean_costs[dataset_id, scale_id, clf_id].tolist()
#                         value = float("{:.2f}".format(mc))
#                         cost_contents[dataset_id][i] = value
#                         i += 1
#                 print(selected_feature_number)
#                 if not os.path.exists("results/experiment1/tables/"):
#                     os.makedirs("results/experiment1/tables/")
#                 acc_df = pd.DataFrame(data=acc_contents, index=datasets, columns=methods_alias)
#                 print("\nACCURACY:\n", acc_df)
#                 filename_acc = "results/experiment1/tables/f%d_%s_acc.tex" % (selected_feature_number, key)
#                 with open(filename_acc, 'w') as f:
#                     f.write(acc_df.to_latex())
#
#                 cost_df = pd.DataFrame(data=cost_contents, index=datasets, columns=methods_alias)
#                 print("\nCOST:\n", cost_df)
#                 filename_cost = "results/experiment1/tables/f%d_%s_cost.tex" % (selected_feature_number, key)
#                 with open(filename_cost, 'w') as f:
#                     f.write(cost_df.to_latex())
# base_clf_alias = np.unique(base_clf_alias)
