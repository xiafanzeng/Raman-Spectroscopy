from keras.utils import Sequence
import numpy as np
import keras.backend as K
from tqdm import tqdm

from config import spectral_shape


class FeatureGen(Sequence):
    def __init__(self, train, data, batch_size=64, verbose=1):
        super(FeatureGen, self).__init__()
        self.data       = data
        self.train      = train
        self.batch_size = batch_size
        self.verbose    = verbose
        if self.verbose > 0: self.progress = tqdm(total=len(self), desc='Features')
        
    def __getitem__(self, index):
        start = self.batch_size*index
        size  = min(len(self.data) - start, self.batch_size)
        a     = np.zeros((size,) + spectral_shape, dtype=K.floatx())
        for i in range(size): a[i,:] = self.train[self.data[start + i]]
        if self.verbose > 0: 
            self.progress.update()
            if self.progress.n >= len(self): self.progress.close()
        return a
    def __len__(self):
        return (len(self.data) + self.batch_size - 1)//self.batch_size
    
    

class ScoreGen(Sequence):
    def __init__(self, x, y=None, batch_size=2048, verbose=1):
        super(ScoreGen, self).__init__()
        self.x          = x
        self.y          = y
        self.batch_size = batch_size
        self.verbose    = verbose
        if y is None:
            self.y           = self.x
            self.ix, self.iy = np.triu_indices(x.shape[0],1)
        else:
            self.iy, self.ix = np.indices((y.shape[0],x.shape[0]))
            self.ix          = self.ix.reshape((self.ix.size,))
            self.iy          = self.iy.reshape((self.iy.size,))
        self.subbatch = (len(self.x) + self.batch_size - 1)//self.batch_size
        if self.verbose > 0: self.progress = tqdm(total=len(self), desc='Scores')
    def __getitem__(self, index):
        start = index*self.batch_size
        end   = min(start + self.batch_size, len(self.ix))
        a     = self.y[self.iy[start:end],:]
        b     = self.x[self.ix[start:end],:]
        if self.verbose > 0: 
            self.progress.update()
            if self.progress.n >= len(self): self.progress.close()
        return [a,b]
    def __len__(self):
        return (len(self.ix) + self.batch_size - 1)//self.batch_size
    
if __name__ == '__main__':
    from utils import load_cache, group_label, shuffle_idxs, score_reshape
    
    train, y_, _, _ = load_cache('../../')
    score = np.random.random_sample(size=(len(train), len(train)))
    id2samples = group_label(y_)
    train_idx, _ = shuffle_idxs(train)
    
    
    from model import build_model
    model, branch_model, head_model = build_model(64e-5,0)
    
    inp = FeatureGen(train, train_idx)
    feats = branch_model.predict(inp[0])
    import ipdb; ipdb.set_trace()
    scoreGen = ScoreGen(feats)
    score = head_model.predict(scoreGen[0])
    res = score_reshape(score, feats)
    print(score.shape)
    