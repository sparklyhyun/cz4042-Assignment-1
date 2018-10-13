
# Find Optimal Learning Rate for 3 layer network designed using 5-fold cross-validation

import tensorflow as tf
import numpy as np
import pylab as plt
from sklearn import model_selection
from sklearn import preprocessing
import multiprocessing as mp

# Proceed to data location
import os
os.chdir('/Users/Charlene/Desktop/REP 4/Neural Networks and Deep Learning/Assignment')

NUM_FEATURES = 8
no_labels=1

# Parameters
epochs = 500
batch_size = 32
num_neuron = 30 # number of neurons in hidden layer
beta=10**-3 # weight decay parameter
no_folds=5 # 5 fold cross validation

# Initialise random seed
seed = 10
np.random.seed(seed)

# Load data from dataset for analysis
cal_housing = np.loadtxt('cal_housing.data', delimiter=',')
X_data, Y_data = cal_housing[:, :8], cal_housing[:, -1]
Y_data = (np.asmatrix(Y_data)).transpose()
idx = np.arange(X_data.shape[0])

# randomly shuffle the idx
np.random.shuffle(idx)
X_data, Y_data = X_data[idx], Y_data[idx]

# experiment with small datasets
X_data, Y_data = X_data[:1000], Y_data[:1000]

# split into testing and validation dataset
trainXV, testXV, trainYV, testYV = model_selection.train_test_split(X_data, Y_data, test_size=0.3, random_state=42)

#Calculate the number of datapoints in a fold
fold_data = int(0.2 * len(trainXV))

#Neural Network
def ffn(x, y_):

    # Hidden layer: Relu Layer
    with tf.name_scope('hidden'):
        w1 = tf.Variable(tf.truncated_normal([NUM_FEATURES, num_neuron], stddev=1.0 / np.sqrt(float(NUM_FEATURES))),
                         name='weights')
        b1 = tf.Variable(tf.zeros([num_neuron]), dtype=tf.float32, name='biases')
        h1 = tf.nn.relu(tf.matmul(x, w1) + b1)

    # Output layer: Linear Layer
    with tf.name_scope('linear'):
        w2 = tf.Variable(tf.truncated_normal([num_neuron, no_labels], stddev=1.0 / np.sqrt(float(num_neuron))),
                         name='weights')
        b2 = tf.Variable(tf.zeros([no_labels]), name='biases')
        prediction = tf.matmul(h1, w2) + b2

    # tabulate the loss
    loss = tf.reduce_mean(tf.reduce_sum(tf.square(y_ - prediction), axis=1))

    # loss with regularisation term
    regularization = tf.nn.l2_loss(w1) + tf.nn.l2_loss(w2)
    losswithreg = tf.reduce_mean(loss + beta * regularization)

    return losswithreg, loss

# Training with different learning rates
def train(learning_rate):

    cv_err=[]

    # Use 5-fold Cross Validation
    for fold in range (no_folds):
        # Taking 1 fold
        start, end=fold*fold_data,(fold+1)*fold_data
        testX, testY = trainXV[start:end], trainYV[start:end]
        trainX = np.append(trainXV[:start], trainXV[end:], axis=0)
        trainY = np.append(trainYV[:start], trainYV[end:], axis=0)

        trainY_ = trainY.reshape(len(trainY), no_labels)
        testY_ = testY.reshape(len(testY), no_labels)

        # standardise the input data
        scaler = preprocessing.StandardScaler()
        trainX_ = scaler.fit_transform(trainX)
        testX_ = scaler.transform(testX)

        # Define the placeholder value
        x = tf.placeholder(tf.float32, [None, NUM_FEATURES])
        y_ = tf.placeholder(tf.float32, [None, no_labels])

        # Create the model
        losswithreg, loss=ffn(x,y_)

        # Create the gradient descent optimizer with the given learning rate.
        train_op = tf.train.GradientDescentOptimizer(learning_rate).minimize(losswithreg)

        N=len(trainX_)
        idx=np.arange(N)

        # Start the session
        with tf.Session() as sess:

            sess.run(tf.global_variables_initializer())
            test_err = []
            batch_test_err=[]

            # Iterate through a number of epochs
            for i in range(epochs):
                np.random.shuffle(idx)
                trainXX=trainX_[idx]
                trainYY=trainY_[idx]

                # Use mini-batch gradient descent learning
                for start, end in zip(range(0, N, batch_size), range(batch_size, N, batch_size)):
                    train_op.run(feed_dict={x: trainXX[start:end], y_: trainYY[start:end]})

                    # Error for 1 batch
                    batch_test_err.append(loss.eval(feed_dict={x: testX_, y_: testY_}))

                # Error for epochs: Mean Batch Error
                test_err.append(sum(batch_test_err)/len(batch_test_err))

        # Error for 1 fold
        cv_err.append(test_err)

    # Mean error across all folds
    cv_err=np.mean(np.array(cv_err),axis=0)

    return cv_err

def main():

    # test out different learning rates
    no_threads=mp.cpu_count()
    learning_rate = [0.5*10**-6, 10 ** -7, 0.5*10**- 8, 10**-9, 10 ** -10]
    p=mp.Pool(processes=no_threads)
    cv_err= p.map(train, learning_rate)

    # plot learning curves
    plt.figure(1)
    for i in range(len(learning_rate)):
        plt.plot(range(epochs), cv_err[i], label= 'Learning Rate= {}'.format(learning_rate[i]))

    plt.xlabel('Number of Epochs')
    plt.ylabel('Mean Cross-Validation Error')
    # also the values for y is very high
    plt.title('3 Layer Feedforward Neural Network, GD Learning')
    plt.legend()
    plt.show()

    # Compare the final CV Errors across Learning Rates after a certain number of epochs
    cv_err=np.array(cv_err)
    cv_err_final=cv_err[: , epochs-1]

    plt.figure(2)
    plt.plot(learning_rate, cv_err_final)
    plt.xlabel('Learning Rate')
    plt.ylabel('Final Cross-Validation Error')
    plt.title('Comparison of Final Cross-Validation Errors with Different Learning Rates')
    plt.show()

    # Optimal learning rate is the one that gives the lowest CV error
    bestlr=learning_rate[np.argmin(cv_err_final)]
    print('learning rate that gives lowest error: {}'.format(bestlr))

    # Split the training and test set again
    trainXV, testXV, trainYV, testYV = model_selection.train_test_split(X_data, Y_data, test_size=0.3, random_state=42)

    # Standardise test data
    stdtrainXV= (trainXV-np.mean(trainXV,axis=0))/np.std(trainXV, axis=0)
    stdtestXV= (testXV- np.mean(trainXV, axis=0))/ np.std(trainXV, axis=0)


    # Define placeholders
    x = tf.placeholder(tf.float32, [None, NUM_FEATURES])
    y_ = tf.placeholder(tf.float32, [None, no_labels])

    # Build the model
    losswithreg, loss= ffn(x,y_)
    train_op = tf.train.GradientDescentOptimizer(bestlr).minimize(losswithreg)

    N = len(stdtrainXV)
    idx = np.arange(N)

    #Start the session and record test errors
    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())

        test_err=[]
        for i in range(epochs):
            # randomly shuffle the training set
            np.random.shuffle(idx)
            stdtrainXV=stdtrainXV[idx]

            batch_test_err = []
            for start, end in zip(range(0, N, batch_size), range(batch_size, N, batch_size)):
                # train it again with the training set 70%
                train_op.run(feed_dict={x: stdtrainXV[start:end], y_: trainYV[start:end]})

                #Tests error for 1 batch
                batch_test_err.append(loss.eval(feed_dict={x: stdtestXV, y_:testYV}))

            #Test error for epochs: Mean batch error
            test_err.append(sum(batch_test_err)/len(batch_test_err))

    plt.figure(3)
    plt.plot(range(epochs), test_err, label='Learning Rate= {}'.format(bestlr))
    plt.xlabel('Number of Epochs')
    plt.ylabel('Mean Test Error')
    plt.title('3 Layer Feedforward Neural Network, GD Learning')
    plt.legend()
    plt.show()


if __name__ == '__main__':
  main()
