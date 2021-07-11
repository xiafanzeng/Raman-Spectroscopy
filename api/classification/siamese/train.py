import numpy as np
import keras.backend as K
from utils import load_cache, group_label, shuffle_idxs, score_reshape, get_lr, set_lr

from datagen import TrainingData
from score import ScoreGen, FeatureGen
from model import build_model

def make_steps(step, ampl):
    global steps, histories, train, id2samples, train_idx
        
    # Compute the match score for each picture pair
    features = branch_model.predict(FeatureGen(train, train_idx, verbose=1), max_queue_size=12, workers=6, verbose=0)
    score    = head_model.predict(ScoreGen(features, verbose=1), max_queue_size=12, workers=6, verbose=0)
    score    = score_reshape(score, features)
    
    # score = np.random.random_sample(size=(len(train), len(train)))
    
    # Train the model for 'step' epochs
    history = model.fit(
        TrainingData(score + ampl*np.random.random_sample(size=score.shape), train, id2samples, train_idx, steps=step, batch_size=32),
        initial_epoch=steps, epochs=steps + step, max_queue_size=12, workers=6, verbose=0,
        # callbacks=[
        #     # TQDMNotebookCallback(leave_inner=True, metric_format='{value:0.3f}')
        # ]
        ).history
    steps += step
    
    # Collect history data
    history['epochs'] = steps
    history['ms'    ] = np.mean(score)
    history['lr'    ] = get_lr(model)
    print(history['epochs'],history['lr'],history['ms'])
    histories.append(history)
    
    
if __name__ == '__main__':
    train, y_, _, _ = load_cache('../../')
    model, branch_model, head_model = build_model(1e-6, 0)
    id2samples = group_label(y_)
    train_idx, _ = shuffle_idxs(train)
    
    histories  = []
    steps      = 0
        
    make_steps(10, 1000)
    ampl = 100.0
    for _ in range(10):
        print('noise ampl.  = ', ampl)
        make_steps(5, ampl)
        ampl = max(1.0, 100**-0.1*ampl)
    # epoch -> 150
    for _ in range(18): make_steps(5, 1.0)
    # epoch -> 200
    set_lr(model, 16e-5)
    for _ in range(10): make_steps(5, 0.5)
    # epoch -> 240
    set_lr(model, 4e-5)
    for _ in range(8): make_steps(5, 0.25)
    # epoch -> 250
    set_lr(model, 1e-5)
    for _ in range(2): make_steps(5, 0.25)
    # epoch -> 300
    weights = model.get_weights()
    model, branch_model, head_model = build_model(64e-5, 0.0002)
    model.set_weights(weights)
    for _ in range(10): make_steps(5, 1.0)
    # epoch -> 350
    set_lr(model, 16e-5)
    for _ in range(10): make_steps(5, 0.5)    
    # epoch -> 390
    set_lr(model, 4e-5)
    for _ in range(8): make_steps(5, 0.25)
    # epoch -> 400
    set_lr(model, 1e-5)
    for _ in range(2): make_steps(5, 0.25)
    model.save('siamese.h5')