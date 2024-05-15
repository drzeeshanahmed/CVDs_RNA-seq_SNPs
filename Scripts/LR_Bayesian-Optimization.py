# Imports --------------
from hyperopt import hp, STATUS_OK, fmin, tpe, Trials, space_eval
from hyperopt.pyll.base import scope
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score
import pandas as pd
import numpy as np
# ----------------------

# Datasets
CIGT = pd.read_csv('/home/wbd20/Ahmed/Results/SNVs_DE_CIGT.csv')
Cohort_Training = pd.read_csv('/home/wbd20/Ahmed/Results/Cohort_Training.csv')

CIGT_Training = CIGT[CIGT['RNASeq'].isin(Cohort_Training['ID'])]
X_train = CIGT_Training.drop(['Type', 'RNASeq', 'WGS'], axis = 1)
y_train = CIGT_Training['Type']

# Parameters
space = {
    'C': hp.loguniform('C', np.log(1e-5), np.log(1e5)),
    'penalty': hp.choice('penalty', ['l2', {'type': 'l1'}, {'type': 'elasticnet', 'l1_ratio': hp.uniform('l1_ratio', 0, 1)}]),
    'solver': hp.choice('solver', ['newton-cg', 'lbfgs', 'liblinear', 'sag', 'saga']),
    'max_iter': scope.int(hp.quniform('max_iter', 100, 5000, 50))
}

# Objectives
def objectives(params):
    if isinstance(params['penalty'], dict):
        penalty_type = params['penalty']['type']
        if penalty_type == 'elasticnet':
            params['solver'] = 'saga'
            params['l1_ratio'] = params['penalty']['l1_ratio']
        elif penalty_type == 'l1':
            params['solver'] = 'saga'
        params['penalty'] = penalty_type
    else:
        if params['penalty'] == 'none' or params['penalty'] == 'l2':
            if params['solver'] == 'liblinear':
                params['solver'] = 'lbfgs'
    
    clf = LogisticRegression(**params, n_jobs = -1)
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