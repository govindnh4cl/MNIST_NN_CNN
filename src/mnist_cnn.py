seed = 1337  # for reproducibility
import numpy as np
np.random.seed(seed)        # Seed Numpy
import random               # Seed random
random.seed(seed)
import tensorflow as tf
tf.set_random_seed(seed)    # Seed Tensor Flow

from keras.models import Sequential, load_model
from keras.layers import Dense, Convolution2D, MaxPooling2D, Flatten, Dropout, BatchNormalization, Activation
from keras.callbacks import ModelCheckpoint
from keras.optimizers import RMSprop
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split


from dataset import read_MNIST

def get_model(input_shape, nb_classes):
    m = Sequential()
    m.add(Convolution2D(8, 3, 3, border_mode='same', input_shape=input_shape, init='he_normal'))
    m.add(BatchNormalization())
    m.add(Activation('relu'))
    m.add(MaxPooling2D(pool_size=(2, 2)))
    m.add(Dropout(0.2))
    m.add(Convolution2D(16, 3, 3, border_mode='same', init='he_normal'))
    m.add(BatchNormalization())
    m.add(Activation('relu'))
    m.add(MaxPooling2D(pool_size=(2, 2)))
    m.add(Dropout(0.2))
    m.add(Convolution2D(16, 3, 3, border_mode='same', init='he_normal'))
    m.add(BatchNormalization())
    m.add(Activation('relu'))
    m.add(MaxPooling2D(pool_size=(2, 2)))
    m.add(Dropout(0.2))
    m.add(Flatten())
    m.add(Dense(128, init='he_normal'))
    m.add(BatchNormalization())
    m.add(Activation('relu'))
    m.add(Dropout(0.1))
    m.add(Dense(64, init='he_normal'))
    m.add(BatchNormalization())
    m.add(Activation('relu'))
    m.add(Dropout(0.1))
    m.add(Dense(nb_classes, init='he_normal'))  # Last layer with one output per
    # m.add(BatchNormalization())
    m.add(Activation('softmax'))

    return m

if __name__ == '__main__':
    nb_classes = 10
    ht = wd = 28
    model_file = 'model.h5'
    epochs = 100
    train = 1

    ############# get data ############
    X_train, y_train = read_MNIST('training', 'resources')
    X_test, y_test = read_MNIST('testing', 'resources')

    ## Data normalization
    # mean_image = np.mean(X_train, axis=0)
    # # s_image = np.std(X_train, axis=0)
    # X_train = (X_train - mean_image)
    # X_train = X_train - np.min(X_train) # lowest pt making 0
    # X_train = (2 * X_train / np.max(X_train) - 1.)
    #
    # X_test = (X_test - mean_image)
    # X_test = X_test - np.min(X_test) # lowest pt making 0
    # X_test = (2 * X_test / np.max(X_test) - 1.)

    X_train, X_val, y_train, y_val = train_test_split(
        X_train, y_train, test_size = 10000, random_state = 42)
    # train-val split
    X_val = X_train[-10000:]
    y_val = y_train[-10000:]
    X_train = X_train[:-10000]
    y_train = y_train[:-10000]


    if train:
        ########## Model creation ###############
        # Model definition
        input_shape = (1, ht, wd)
        m = get_model(input_shape, nb_classes)

        ################### Training #############
        opt = RMSprop()

        # Compile
        m.compile(loss='categorical_crossentropy', optimizer=opt, metrics=["accuracy"])

        # Train
        checkpointer = ModelCheckpoint(filepath=model_file,
                                       monitor='val_loss', verbose=1, save_best_only=True)

        hist = m.fit(X_train, y_train,
              batch_size=256, nb_epoch=epochs,
              validation_data=(X_val, y_val), callbacks=[checkpointer])

        # write history
        np.save('history.npy', hist.history)
        training_loss = hist.history['loss']
        training_acc = hist.history['acc']

        plt.figure()
        plt.grid()
        plt.title('Loss vs Epochs')  # summarize history for accuracy
        plt.ylabel('Loss')
        plt.xlabel('Epoch')
        legend = ['Training Loss', 'Validation Loss']
        plt.plot(hist.history['loss'], linewidth=1)
        plt.plot(hist.history['val_loss'], linewidth=1)
        plt.legend(legend, loc='best')
        plt.show(block=0)

        plt.figure()
        plt.grid()
        plt.title('Accuracy vs Epochs')  # summarize history for accuracy
        plt.ylabel('Accuracy')
        plt.xlabel('Epoch')
        legend = ['Training Accuracy', 'Validation Accuracy']
        plt.plot(100*np.array(hist.history['acc']), linewidth=1)
        plt.plot(100*np.array(hist.history['val_acc']), linewidth=1)
        plt.legend(legend, loc='best')
        plt.show(block=1)

    ################### Testing #############
    m = load_model(model_file)
    print(m.summary())
    test_result = m.evaluate(X_test, y_test)
    print(test_result)






