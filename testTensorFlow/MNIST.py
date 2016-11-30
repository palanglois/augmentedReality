#!/usr/bin/python

#Load matplotlib
import matplotlib.pyplot as plt
plt.style.use('ggplot')

#Loading the mnist data
from tensorflow.examples.tutorials.mnist import input_data
mnist = input_data.read_data_sets('MNIST_data', one_hot=True)

import tensorflow as tf
sess = tf.InteractiveSession()

#Allocating sizes for the images
x = tf.placeholder(tf.float32, shape=[None, 784])
y_ = tf.placeholder(tf.float32, shape=[None, 10])

#Initializing the weight and bias
W = tf.Variable(tf.zeros([784,10]))
b = tf.Variable(tf.zeros([10]))

#Performing the initialization in the back-end
sess.run(tf.global_variables_initializer())

#Regression model : 
y = tf.matmul(x,W) + b

#Using cross-entropy as a loss function
cross_entropy = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(y, y_))

#Defining the learning rate
learningRate = 0.5

#Training
train_step = tf.train.GradientDescentOptimizer(learningRate).minimize(cross_entropy)

#Doing 1000 training steps
iterations = []
for i in range(1000):
  batch = mnist.train.next_batch(784)
  _, loss_val =  sess.run([train_step,cross_entropy], feed_dict={x: batch[0], y_: batch[1]})
  iterations.append(loss_val)

plt.plot(iterations)
plt.show()

#Number of correct prediction
correct_prediction = tf.equal(tf.argmax(y,1), tf.argmax(y_,1))
accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))
print(accuracy.eval(feed_dict={x: mnist.test.images, y_: mnist.test.labels}))


