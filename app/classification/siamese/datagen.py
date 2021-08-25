try:
    from lapjv import lapjv
    # from scipy.optimize import linear_sum_assignment
    segment = False
except ImportError:
    print('Module lap not found, emulating with much slower scipy.optimize.linear_sum_assignment')
    segment = True
    from scipy.optimize import linear_sum_assignment

import random
import numpy as np
import keras.backend as K
from keras.utils import Sequence

class TrainingData(Sequence):
    def __init__(self, score, train, id2samples, train_idx, steps=1000, batch_size=32):
        super(TrainingData, self).__init__()
        # Maximizing the score is the same as minimuzing -score.
        self.score      = -score 
        self.train      = train
        self.dims       = train.shape[1]
        self.steps      = steps
        self.batch_size = batch_size
        self.id2samples = id2samples
        self.train_idx = train_idx
        
        t2i = {}
        for i,t in enumerate(train_idx): t2i[t] = i
        
        for ts in id2samples.values():
            idxs = [t2i[t] for t in ts]
            for i in idxs:
                for j in idxs:
                    # Set a large value for matching whales -- eliminates this potential pairing
                    self.score[i,j] = 10000.0 
                    
        self.on_epoch_end()
    
    def on_epoch_end(self):
        # Skip this on the last epoch.
        if self.steps <= 0: return 
        
        self.steps     -= 1
        self.match      = []
        self.unmatch    = []

        if segment:
            # Using slow scipy. Make small batches.
            tmp   = []
            batch = 512
            for start in range(0, score.shape[0], batch):
                end = min(score.shape[0], start + batch)
                _, x = linear_sum_assignment(self.score[start:end, start:end])
                tmp.append(x + start)
            x = np.concatenate(tmp)
        else:        
            # Solve the linear assignment problem
            
            # _,_, x = lapjv(self.score) 
            # import ipdb; ipdb.set_trace()
            x, _, _ = lapjv(self.score)
            
        y = np.arange(len(x), dtype=np.int32)

        # Compute a derangement for matching whales
        for ts in self.id2samples.values():
            d = ts.copy()
            while True:
                random.shuffle(d)
                if not np.any(ts == d): break
            for ab in zip(ts, d): self.match.append(ab)
        
        if 1:
            # Construct unmatched pairs from the LAP solution.
            for i,j in zip(x,y):
                if i == j:
                    print(f'i {i} == j {j}')
                    # print(self.score)
                    print(x)
                    print(y)
                assert i != j
                self.unmatch.append((self.train_idx[i], self.train_idx[j]))

            # Force a different choice for an eventual next epoch.
            self.score[x,y] = 10000.0
            self.score[y,x] = 10000.0
            
        random.shuffle(self.match)
        random.shuffle(self.unmatch)
        
        assert len(self.match) == len(self.train) and len(self.unmatch) == len(self.train)
        
    def __len__(self):
        return (len(self.match) + len(self.unmatch) + self.batch_size - 1) // self.batch_size
    
    def __getitem__(self, index):
        start = self.batch_size * index
        end   = min(start + self.batch_size, len(self.match) + len(self.unmatch))
        size  = end - start
        assert size > 0
        
        a     = np.zeros((size,) + (self.dims,), dtype=K.floatx())
        b     = np.zeros((size,) + (self.dims,), dtype=K.floatx())
        c     = np.zeros((size,1), dtype=K.floatx())
        j     = start//2
        
        for i in range(0, size, 2):
            a[i,  :] = self.train[self.match[j][0]]
            b[i,  :] = self.train[self.match[j][1]]
            # This is a match
            c[i,  0] = 1 

            a[i+1,:] = self.train[self.unmatch[j][0]]
            b[i+1,:] = self.train[self.unmatch[j][1]]
            # unmatch
            c[i+1,0] = 0 
            j           += 1
        return [a[:,None,],b[:,None,]],c    


if __name__ == '__main__':
    from utils import load_cache, group_label, shuffle_idxs
    
    train, y_, _, _ = load_cache('../../')
    score = np.random.random_sample(size=(len(train), len(train)))
    id2samples = group_label(y_)
    train_idx, _ = shuffle_idxs(train)
    
    data = TrainingData(score, train, id2samples, train_idx)
    import ipdb; ipdb.set_trace()
    print(data)