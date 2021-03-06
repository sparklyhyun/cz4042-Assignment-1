import math
import tensorflow as tf
import numpy as np
import pylab as plt
import os
import time

#create plots folder, remove comment later
if not os.path.isdir('plots'):
    print('create figures folder')
    os.makedirs('plots')

# scale data
def scale(X, X_min, X_max):
    return (X - X_min)/(X_max-X_min)

NUM_FEATURES = 36
NUM_CLASSES = 6

learning_rate = 0.01
epochs = 1000
batch_size = 16
num_neurons = 15   #hidden layer neurons 
seed = 10
np.random.seed(seed)
decay_param = [0, 10**-3, 10**-6, 10**-9, 10**-12]

#read train data
train_input = np.loadtxt('sat.trn',delimiter=' ')
trainX, train_Y = train_input[:,:36], train_input[:,-1].astype(int)                      
trainX = scale(trainX, np.min(trainX, axis=0), np.max(trainX, axis=0))  
train_Y[train_Y == 7] = 6                                                                                    

trainY = np.zeros((train_Y.shape[0], NUM_CLASSES)) 
trainY[np.arange(train_Y.shape[0]), train_Y-1] = 1

print('train data read')

#read test data
test_input = np.loadtxt('sat.tst', delimiter = ' ')
testX, test_Y = test_input[:, :36], test_input[:, -1].astype(int)
testX = scale(testX, np.min(testX, axis = 0), np.max(testX, axis = 0))
test_Y[test_Y == 7] = 6

testY = np.zeros((test_Y.shape[0], NUM_CLASSES))
testY[np.arange(test_Y.shape[0]), test_Y-1] = 1 #one hot matrix, K 

print('test data read')

# experiment with small datasets
'''
trainX = trainX[:1000]
trainY = trainY[:1000]
testX = testX[:1000]
testY = testY[:1000]
'''

# model input & output , x = input, y_ = output
x = tf.placeholder(tf.float32, [None, NUM_FEATURES])        
y_ = tf.placeholder(tf.float32, [None, NUM_CLASSES]) 
  

#Initializing weights and biases for hidden perceptron layer & output softmax layer 
weights = {
    #from input to hidden layer
    'w1' : tf.Variable(tf.truncated_normal([NUM_FEATURES, num_neurons],
                                   stddev  = 1.0/math.sqrt(float(NUM_FEATURES)))),
    #from hidden layer to output layer
    'out' : tf.Variable(tf.truncated_normal([num_neurons, NUM_CLASSES],
                                   stddev  = 1.0/math.sqrt(float(num_neurons)))) 
    }

biases = {
    #from input to hidden layer
    'b1' : tf.Variable(tf.zeros([num_neurons])),
    #from hidden layer  to output layer
    'out' : tf.Variable(tf.zeros([NUM_CLASSES]))
    }

def network_3_layer(x):
    hidden1 = tf.add(tf.matmul(x, weights['w1']), biases['b1'])
    hidden1_out = tf.sigmoid(hidden1)
    output = tf.matmul(hidden1_out, weights['out']) + biases['out']
    return output 

logits = network_3_layer(x)

# running training & testing 
err_= [[],[],[],[],[]]
err_batch = []
acc_test = [[],[],[],[],[]]
training_time = [[],[],[],[],[]]

print('test once per epoch')

def decay_param_training(a, d):
    #Cost function (softmax)
    cross_entropy = tf.nn.softmax_cross_entropy_with_logits_v2(labels=y_, logits=logits) 
    loss = tf.reduce_mean(cross_entropy)
    
    #implementing l2 regularizer for 3 layer network
    regularizer = tf.nn.l2_loss(weights['w1']) + tf.nn.l2_loss(weights['out'])
    loss = tf.reduce_mean(loss+ d * regularizer)

    # Create the gradient descent optimizer with the given learning rate.
    optimizer = tf.train.GradientDescentOptimizer(learning_rate)
    train_op = optimizer.minimize(loss)

    correct_prediction = tf.cast(tf.equal(tf.argmax(logits, 1), tf.argmax(y_, 1)), tf.float32)
    accuracy = tf.reduce_mean(correct_prediction)
    
    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())
        #need to change the batch size 
        trainX_batch = [trainX[i * batch_size : (i +1) * batch_size]
                    for i in range((trainX.shape[0] + batch_size -1)// batch_size)]
        trainY_batch = [trainY[i * batch_size : (i +1) * batch_size]
                    for i in range((trainY.shape[0] + batch_size -1)// batch_size)]
        training_time_1 = 0;
        for i in range(epochs):
            #batch'
            start = time.time() #time taken to train 1 epoch
            for j in range(len(trainX_batch)):
                train_op.run(feed_dict={x: trainX_batch[j], y_: trainY_batch[j]})
                err_batch.append(loss.eval(feed_dict = {x: trainX_batch[j], y_: trainY_batch[j]}))

            training_time_1 += time.time() - start
                
            
            err_[a].append(sum(err_batch)/len(err_batch))
            err_batch[:] = []

            #test
            acc_test[a].append(accuracy.eval(feed_dict = {x: testX, y_:testY}))

            if i % 100 == 0:
                print('iter %d: accuracy %g error:%g'%(i, acc_test[a][i], err_[a][i]))
        print('learning & testing done')
        training_time[a] = training_time_1 / epochs
        print('time taken to train 1 epoch %f' %(training_time[a]) )
    return 

decay_param_training(0, decay_param[0]) #decay_param = 0
decay_param_training(1, decay_param[1]) #decay_param = 0**-3
decay_param_training(2, decay_param[2]) #decay_param = 10**-6
decay_param_training(3, decay_param[3]) #decay_param = 10**-9
decay_param_training(4, decay_param[4]) #decay_param = 10**-12

# plot Q2 - training errors against no. of epoch
plt.figure(1)
plt.plot(range(epochs), err_[0])
plt.plot(range(epochs), err_[1])
plt.plot(range(epochs), err_[2])
plt.plot(range(epochs), err_[3])
plt.plot(range(epochs), err_[4])
plt.xlabel(str(epochs) + 'iterations')
plt.ylabel('classification error')
plt.legend(['decay_param = 0', 'decay_param = 10**-3', 'decay_param = 10**-6', 'decay_param = 10**-9', 'decay_param = 10**-12'])
#plt.legend(['decay_param = 0', 'decay_param = 10**-3'])
plt.title('Q4. training error')
plt.savefig('plots/Qn4(1).png')

#plot Q2 - test accurcy against no. of epoch
plt.figure(2)
plt.plot(range(epochs), acc_test[0])
plt.plot(range(epochs), acc_test[1])
plt.plot(range(epochs), acc_test[2])
plt.plot(range(epochs), acc_test[3])
plt.plot(range(epochs), acc_test[4])
plt.xlabel(str(epochs) + 'iterations')
plt.ylabel('test accuracy')
plt.legend(['decay_param = 0', 'decay_param = 10**-3', 'decay_param = 10**-6', 'decay_param = 10**-9', 'decay_param = 10**-12'])
#plt.legend(['decay_param = 0', 'decay_param = 10**-3'])
plt.title('Q4. test accuracy')
plt.savefig('plots/Qn4(2).png')

'''
#plot Q2 - training tme against each bath size
plt.figure(3)
plt.plot(range(len(decay_param)), training_time)
plt.xticks(range(len(decay_param)), decay_param)
plt.xlabel('decay parameter')
plt.ylabel('training time')
#plt.legend(['batch size = 4', 'batch size = 8'])
plt.title('Q4. training time')
#plt.savefig('plots/Qn4(2).png')
'''
plt.show()
