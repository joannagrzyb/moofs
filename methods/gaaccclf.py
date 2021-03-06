from pymoo.algorithms.so_genetic_algorithm import GA
from pymoo.optimize import minimize
from pymoo.factory import get_crossover, get_mutation, get_sampling

from sklearn.base import ClassifierMixin, BaseEstimator

from methods.optimization.optimizationAcc import FeatureSelectionAccuracyProblem


class GeneticAlgorithmAccuracyClf(BaseEstimator, ClassifierMixin):
    def __init__(self, base_estimator, scale_features=0.5, test_size=0.5, objectives=1, p_size=100, c_prob=0.1, m_prob=0.1):
        self.base_estimator = base_estimator
        self.test_size = test_size
        self.p_size = p_size
        self.c_prob = c_prob
        self.m_prob = m_prob
        self.objectives = objectives
        self.scale_features = scale_features

        self.estimator = None
        self.res = None
        self.selected_features = None
        self.feature_costs = None

    def fit(self, X, y):
        features = range(X.shape[1])
        problem = FeatureSelectionAccuracyProblem(X, y, self.test_size, self.base_estimator, features, self.scale_features, self.objectives)

        algorithm = GA(
                       pop_size=self.p_size,
                       sampling=get_sampling("bin_random"),
                       crossover=get_crossover("bin_hux"),
                       mutation=get_mutation("bin_bitflip"),
                       eliminate_duplicates=True)

        res = minimize(
                       problem,
                       algorithm,
                       ('n_eval', 1000),
                       seed=1,
                       verbose=False,
                       save_history=True)

        self.selected_features = res.X
        self.estimator = self.base_estimator.fit(X[:, self.selected_features], y)
        return self

    def predict(self, X):
        return self.estimator.predict(X[:, self.selected_features])

    def predict_proba(self, X):
        return self.estimator.predict_proba(X[:, self.selected_features])

    def selected_features_cost(self):
        total_cost = 0
        for id, cost in enumerate(self.feature_costs):
            if self.selected_features[id]:
                total_cost += cost
        return total_cost
