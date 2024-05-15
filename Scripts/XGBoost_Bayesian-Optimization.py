# Imports --------------
# 
from hyperopt import hp, STATUS_OK, fmin, tpe, Trials
from hyperopt.pyll.base import scope
from xgboost import XGBClassifier
from sklearn.model_selection import cross_val_score
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
    'max_depth': scope.int(hp.quniform('max_depth', 3, 10, 1)),
    'min_child_weight': hp.quniform('min_child_weight', 1, 10, 1),
    'gamma': hp.uniform('gamma', 0, 0.4),
    'subsample': hp.uniform('subsample', 0.5, 1.0),
    'colsample_bytree': hp.uniform('colsample_bytree', 0.5, 1.0),
    'scale_pos_weight': hp.uniform('scale_pos_weight', 1, 10),
    'n_estimators': scope.int(hp.quniform('n_estimators', 100, 5000, 50)),
    'learning_rate': hp.uniform('learning_rate', 0.01, 0.2)
}

# Objectives
def objectives(params):
    params['max_depth'] = int(params['max_depth'])
    params['min_child_weight'] = int(params['min_child_weight'])
    
    clf = XGBClassifier(**params, use_label_encoder=False, eval_metric='logloss', n_jobs = -1)
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