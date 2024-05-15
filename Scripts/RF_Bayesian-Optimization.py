# Imports --------------
from hyperopt import hp, STATUS_OK
from hyperopt.pyll.base import scope
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score
from hyperopt import fmin, tpe, Trials
import pandas as pd
# ----------------------

# Datasets
CIGT = pd.read_csv('/home/wbd20/Ahmed/Results/SNVs_DE_CIGT.csv')
Cohort_Training = pd.read_csv('/home/wbd20/Ahmed/Results/Cohort_Training.csv')

CIGT_Training = CIGT[CIGT['RNASeq'].isin(Cohort_Training['ID'])]
X_train = CIGT_Training.drop(['Type', 'RNASeq', 'WGS'], axis = 1)
y_train = CIGT_Training['Type']

# Parameters
space = {
    'max_depth': scope.int(hp.quniform('max_depth', 1, 20, 1)),
    'min_samples_split': scope.int(hp.quniform('min_samples_split', 2, 20, 1)),
    'min_samples_leaf': scope.int(hp.quniform('min_samples_leaf', 1, 10, 1)),
    'n_estimators': scope.int(hp.quniform('n_estimators', 100, 5000, 50)),
    'max_features': hp.choice('max_features', ['sqrt', 'log2', None]),
    'bootstrap': hp.choice('bootstrap', [True, False]),
    'criterion': hp.choice('criterion', ['gini', 'entropy', 'log_loss']),
    'max_leaf_nodes': scope.int(hp.quniform('max_leaf_nodes', 2, 20, 1)),
    'max_samples': hp.uniform('max_samples', 0.01, 0.5)
}

# Objectives
def objectives(params):
    params['max_depth'] = int(params['max_depth'])
    params['min_samples_split'] = int(params['min_samples_split'])
    params['min_samples_leaf'] = int(params['min_samples_leaf'])
    params['n_estimators'] = int(params['n_estimators'])
    params['max_leaf_nodes'] = int(params['max_leaf_nodes'])
    
    if not params['bootstrap']:
        params.pop('max_samples', None)
    
    clf = RandomForestClassifier(**params, n_jobs=-1)
    score = cross_val_score(clf, X_train, y_train, cv = 10, scoring='neg_log_loss').mean()
    return {'loss': -score, 'status': STATUS_OK}

# Trials
trials = Trials()

best_clf = fmin(
    fn = objectives,
    space = space,
    algo = tpe.suggest,
    max_evals = 1000,
    trials = trials
)

# Results
print("Best parameters:", best_clf)