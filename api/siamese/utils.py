import random
import pickle

import numpy as np
import keras.backend as K

from collections import defaultdict


def group_label(y_):
    id2samples = defaultdict(list)
    for i, _id in enumerate(y_):
        id2samples[_id].append(i)

    for _id, samples in id2samples.items(): id2samples[_id] = np.array(samples)
    return id2samples


def shuffle_idxs(train):
    train_idx = list(range(len(train)))
    random.shuffle(train_idx)
    t2i = {}
    for i,t in enumerate(train_idx): t2i[t] = i
    
    return train_idx, t2i


def load_cache(folder):
    obj = pickle.load(open(folder + 'obj.pkl', 'rb'))
    return np.load(folder + 'train.npy'), obj['y_'], obj['label2id'], obj['id2label']


def score_reshape(score, x, y=None):
    if y is None:
        # When y is None, score is a packed upper triangular matrix.
        # Unpack, and transpose to form the symmetrical lower triangular matrix.
        m = np.zeros((x.shape[0],x.shape[0]), dtype=K.floatx())
        m[np.triu_indices(x.shape[0],1)] = score.squeeze()
        m += m.transpose()
    else:
        m        = np.zeros((y.shape[0],x.shape[0]), dtype=K.floatx())
        iy,ix    = np.indices((y.shape[0],x.shape[0]))
        ix       = ix.reshape((ix.size,))
        iy       = iy.reshape((iy.size,))
        m[iy,ix] = score.squeeze()
    return m

def set_lr(model, lr):
    K.set_value(model.optimizer.lr, float(lr))

def get_lr(model):
    return K.get_value(model.optimizer.lr)