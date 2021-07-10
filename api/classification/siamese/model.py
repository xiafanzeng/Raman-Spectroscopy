from keras import regularizers
from keras.optimizers import Adam
from keras.engine.topology import Input
from keras.layers import Activation, Add, BatchNormalization, Concatenate, Conv1D, Conv2D, Dense, Flatten, GlobalMaxPooling1D, Lambda, MaxPooling1D, Reshape
from keras.models import Model
import keras.backend as K

from config import spectral_shape

def subblock(x, filter, **kwargs):
    x = BatchNormalization()(x)
    y = x
    y = Conv1D(filter, 1, activation='relu', **kwargs)(y) # Reduce the number of features to 'filter'
    y = BatchNormalization()(y)
    y = Conv1D(filter, 3, activation='relu', **kwargs)(y) # Extend the feature field
    y = BatchNormalization()(y)
    y = Conv1D(K.int_shape(x)[-1], 1, **kwargs)(y) # no activation # Restore the number of original features
    y = Add()([x,y]) # Add the bypass connection
    y = Activation('relu')(y)
    return y

def build_model(lr, l2, activation='sigmoid'):

    ##############
    # BRANCH MODEL
    ##############
    regul  = regularizers.l2(l2)
    optim  = Adam(lr=lr)
    kwargs = {'padding':'same', 'kernel_regularizer':regul}

    inp = Input(shape=spectral_shape) # 1x128
    x   = Conv1D(64, 5, strides=1, activation='relu', **kwargs)(inp)

    # x   = MaxPooling1D((2, 2), strides=(2, 2))(x) # 1x64
    for _ in range(2):
        x = BatchNormalization()(x)
        x = Conv1D(64, 3, activation='relu', **kwargs)(x)

    # x = MaxPooling1D((2, 2), strides=(2, 2))(x) # 48x48x64
    x = BatchNormalization()(x)
    x = Conv1D(128, 1, activation='relu', **kwargs)(x) # 1x128
    for _ in range(4): x = subblock(x, 64, **kwargs)

    # x = MaxPooling1D((2, 2), strides=(2, 2))(x) # 24x24x128
    x = BatchNormalization()(x)
    x = Conv1D(256, 1, activation='relu', **kwargs)(x) # 1x256
    for _ in range(4): x = subblock(x, 64, **kwargs)

    # x = MaxPooling1D((2, 2), strides=(2, 2))(x) # 12x12x256
    # x = BatchNormalization()(x)
    # x = Conv1D(384, (1,1), activation='relu', **kwargs)(x) # 12x12x384
    # for _ in range(4): x = subblock(x, 96, **kwargs)

    # x = MaxPooling1D((2, 2), strides=(2, 2))(x) # 6x6x384
    x = BatchNormalization()(x)
    x = Conv1D(512, 1, activation='relu', **kwargs)(x) # 1x512
    for _ in range(4): x = subblock(x, 128, **kwargs)
    
    x             = GlobalMaxPooling1D()(x) # 512
    branch_model  = Model(inp, x)
    
    ############
    # HEAD MODEL
    ############
    mid        = 32
    xa_inp     = Input(shape=branch_model.output_shape[1:])
    xb_inp     = Input(shape=branch_model.output_shape[1:])
    x1         = Lambda(lambda x : x[0]*x[1])([xa_inp, xb_inp])
    x2         = Lambda(lambda x : x[0] + x[1])([xa_inp, xb_inp])
    x3         = Lambda(lambda x : K.abs(x[0] - x[1]))([xa_inp, xb_inp])
    x4         = Lambda(lambda x : K.square(x))(x3)
    x          = Concatenate()([x1, x2, x3, x4])

    x          = Reshape((4, branch_model.output_shape[1], 1), name='reshape1')(x)
    # Per feature NN with shared weight is implemented using CONV1D with appropriate stride.
    x          = Conv2D(mid, (4, 1), activation='relu', padding='valid')(x)
    x          = Reshape((branch_model.output_shape[1], mid, 1))(x)
    x          = Conv2D(1, (1, mid), activation='linear', padding='valid')(x)
    x          = Flatten(name='flatten')(x)
    
    # Weighted sum implemented as a Dense layer.
    x          = Dense(1, use_bias=True, activation=activation, name='weighted-average')(x)
    head_model = Model([xa_inp, xb_inp], x, name='head')

    ########################
    # SIAMESE NEURAL NETWORK
    ########################
    # Complete model is constructed by calling the branch model on each input image,
    # and then the head model on the resulting 512-vectors.
    img_a      = Input(shape=spectral_shape)
    img_b      = Input(shape=spectral_shape)
    xa         = branch_model(img_a)
    xb         = branch_model(img_b)
    x          = head_model([xa, xb])
    model      = Model([img_a, img_b], x)
    model.compile(optim, loss='binary_crossentropy', metrics=['binary_crossentropy', 'acc'])
    return model, branch_model, head_model

if __name__ == '__main__':
    model, branch_model, head_model = build_model(64e-5,0)