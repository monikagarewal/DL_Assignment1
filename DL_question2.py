# -*- coding: utf-8 -*-
"""DL_Question2.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1cdnyh4gNNrmm6SGhRVvOTQhCxUikciX4
"""

!pip install wandb -qqq
import wandb
wandb.init(project="Back_Propagation", entity="cs20m040")
!wandb login fb3bb8a505ba908b667b747ed68e4b154b2f6fc5

from tqdm.notebook import tqdm
from sklearn.preprocessing import OneHotEncoder
from keras.datasets import fashion_mnist
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors
import pandas as pd
import math

config_defaults={
        'epochs' : 10,
        'batch_size' : 128,
        'learning_rate' : .001,
        'hidden_sizes' : [64]
        
}
wandb.init(config=config_defaults)
config = wandb.config

# give class name for all image categories
class_names = {i:cn for i, cn in enumerate(['T-shirt/top', 'Trouser', 'Pullover', 'Dress', 'Coat',
               'Sandal', 'Shirt', 'Sneaker', 'Bag', 'Ankle boot']) }

#load the dataset
(x_train, y_train), (x_test, y_test) = fashion_mnist.load_data()

# reshape dataset to have a single channel
X_train = x_train.reshape(x_train.shape[0],  1, x_train.shape[1] * x_train.shape[2])
X_test = x_test.reshape(x_test.shape[0],  1, x_test.shape[1] * x_test.shape[2])

# Convert from integers to floats
x_train = x_train.astype(np.float64)
x_test = x_test.astype(np.float64)

# scale the values between 0 and 1 for both training and testing set
x_train = x_train / 255.0
x_test = x_test / 255.0

enc = OneHotEncoder()
# 0 -> (1, 0, 0, 0), 1 -> (0, 1, 0, 0), 2 -> (0, 0, 1, 0), 3 -> (0, 0, 0, 1)
y_OH_train = enc.fit_transform(np.expand_dims(y_train,1)).toarray()
y_OH_val = enc.fit_transform(np.expand_dims(y_test,1)).toarray()

def plot(images, labels, predictions=None):
  # create a grid with 5 columns
    n_cols = min(5, len(images))
    n_rows = math.ceil(len(images) / n_cols)
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(n_cols+3, n_rows+4))
    
    if predictions is None:
        predictions = [None] * len(labels)
      
    # plot images
    for i, (x, y_true, y_pred) in enumerate(zip(images, labels, predictions)):
        # plot all images in a single loop
        ax = axes.flat[i]
        ax.imshow(x, cmap=plt.cm.binary)
        
        ax.set_title(f"Lbl: {class_names[y_true]}")
        
        if y_pred is not None:
            ax.set_xlabel(f"pred: {class_names[y_pred]}")
    
        ax.set_xticks([])
        ax.set_yticks([])
        

 # plot first few images
plot(x_train[:10], y_train[:10])

class FFSN_MultiClass:
  
  def __init__(self, n_inputs, n_outputs, hidden_sizes=[3]):
    self.nx = n_inputs
    self.ny = n_outputs
    self.nh = len(hidden_sizes)
    self.sizes = [self.nx] + hidden_sizes + [self.ny] 

    self.W = {}
    self.B = {}
    for i in range(self.nh+1):
      self.W[i+1] = np.random.randn(self.sizes[i], self.sizes[i+1])
      self.B[i+1] = np.zeros((1, self.sizes[i+1]))
      
  def sigmoid(self, x):
    return 1.0/(1.0 + np.exp(-x))
  
  def softmax(self, x):
    exps = np.exp(x)
    return exps / np.sum(exps)

  def forward_pass(self, x):
    self.A = {}
    self.H = {}
    self.H[0] = x.reshape(1, -1)
    for i in range(self.nh):
      self.A[i+1] = np.matmul(self.H[i], self.W[i+1]) + self.B[i+1]
      self.H[i+1] = self.sigmoid(self.A[i+1])
    self.A[self.nh+1] = np.matmul(self.H[self.nh], self.W[self.nh+1]) + self.B[self.nh+1]
    self.H[self.nh+1] = self.softmax(self.A[self.nh+1])
    return self.H[self.nh+1]

  def grad(self, x, y):
    
    self.forward_pass(x)
    self.dW = {}
    self.dB = {}
    self.dH = {}
    self.dA = {}
    L = self.nh + 1
    self.dA[L] = (self.H[L] - y)
    for k in range(L, 0, -1):
      self.dW[k] = np.matmul(self.H[k-1].T, self.dA[k])
      self.dB[k] = self.dA[k]
      self.dH[k-1] = np.matmul(self.dA[k], self.W[k].T)
      self.dA[k-1] = np.multiply(self.dH[k-1], self.grad_sigmoid(self.H[k-1])) 

  
  def predict(self, X):
    Y_pred = []
    for x in X:
      y_pred = self.forward_pass(x)
      Y_pred.append(y_pred)
    return np.array(Y_pred).squeeze()
 
  def grad_sigmoid(self, x):
    return x*(1-x) 
  
  def cross_entropy(self,label,pred):
    yl=np.multiply(pred,label)
    yl=yl[yl!=0]
    yl=-np.log(yl)
    yl=np.mean(yl)
    return yl
 
 
  def fit(self, X, Y, epochs=10, initialize='True', learning_rate=0.05, display_loss=False):
      
    if display_loss:
      loss = {}
      
    if initialize:
      for i in range(self.nh+1):
        self.W[i+1] = np.random.randn(self.sizes[i], self.sizes[i+1])
        self.B[i+1] = np.zeros((1, self.sizes[i+1]))
        
    for epoch in tqdm(range(epochs), total=epochs, unit="epoch"):
      dW = {}
      dB = {}
      for i in range(self.nh+1):
        dW[i+1] = np.zeros((self.sizes[i], self.sizes[i+1]))
        dB[i+1] = np.zeros((1, self.sizes[i+1]))
      for x, y in zip(X, Y):
        self.grad(x, y)
        for i in range(self.nh+1):
          dW[i+1] += self.dW[i+1]
          dB[i+1] += self.dB[i+1]
                  
      m = X.shape[1]
      for i in range(self.nh+1):
        self.W[i+1] -= learning_rate * (dW[i+1]/m)
        self.B[i+1] -= learning_rate * (dB[i+1]/m)
        
      if display_loss:
        Y_pred = self.predict(X) 
        loss[epoch] = self.cross_entropy(Y, Y_pred)
    
    if display_loss:
      #plt.plot(loss.values())
      plt.plot(np.array(list(loss.values())).astype(float))
      plt.xlabel('Epochs')
      plt.ylabel('Cross Entropy')
      plt.show()

#train the network
from sklearn.metrics import accuracy_score
ffsn_multi = FFSN_MultiClass(X_train.shape[2], y_OH_train.shape[1], hidden_sizes=config.hidden_sizes)
ffsn_multi.fit(x_train, y_OH_train, epochs=config.epochs,
               learning_rate=config.learning_rate, 
               display_loss=True, 
              )

Y_pred_train = ffsn_multi.predict(x_train)
Y_pred_train = np.argmax(Y_pred_train,1)

Y_pred_val = ffsn_multi.predict(x_test)
Y_pred_val = np.argmax(Y_pred_val,1)

accuracy_train = accuracy_score(Y_pred_train, y_train)
accuracy_val = accuracy_score(Y_pred_val, y_test)

print("Training accuracy", round(accuracy_train, 4))
print("Validation accuracy", round(accuracy_val, 4))

# plot 20 random data
rand_idxs = np.random.permutation(len(x_test))[:20]

plot(x_test[rand_idxs], y_test[rand_idxs], Y_pred_val[rand_idxs])