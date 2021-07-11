import numpy as np
import keras.backend as K
from utils import load_cache, group_label, shuffle_idxs, score_reshape, get_lr, set_lr

from datagen import TrainingData
from score import ScoreGen, FeatureGen
from model import build_model 
    
def test(clf, data, y_, n_splits=2):
    
    from sklearn.model_selection import StratifiedKFold
    from sklearn.metrics import f1_score, accuracy_score    
    
    skfold = StratifiedKFold(n_splits=n_splits)
    import pandas
    
    
    y_.index = list(range(len(y_)))
    for train_idx, test_idx in skfold.split(data, y_):
        y = clf.predict(data[test_idx])
        
        f1, acc = f1_score(y_[test_idx], y, average='weighted'), accuracy_score(y_[test_idx], y)
        print(f'f1: {f1}, acc: {acc}')    
    
if __name__ == '__main__':
    train, y_, _, _ = load_cache('../../')
    model, branch_model, head_model = build_model(1e-6, 0)
    
    test(model, train, y_)
    
