# -*- coding: utf-8 -*-
"""DL_Question-3&4.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1kkGkiOhmtoqwWQs3DIAWZs5PyuD9iRrD
"""

!pip install wandb -qqq
import wandb
wandb.init(project="Back_Propagation", entity="cs20m040")
!wandb login fb3bb8a505ba908b667b747ed68e4b154b2f6fc5

sweep_config = {
      'method' : 'random',
      'metric' : {
          'name' : 'accuracy',
          'goal' : 'maximize'
      },
      'parameters' : {
          'epochs' : {'values' : [5, 10, 15]},
          'batch_size' : {'values' : [32, 64, 128]},
          'learning_rate' : {'values' : [0.001, 0.0001, 0.01, 0.05, 0.02]},
          'hidden_layers' : {'values' : [3, 4, 5]},
          'sizes' : {'values' : [64, 128]},
          'weight_decay' : {'values' : [0, 0.0005, 0.5]},
          'opt_algo' : {'values' : ['gd', 'sgd', 'nag', 'mgd', 'rmsprop', 'adam', 'nadam']},
          'init_method' : {'values' : ['random','xavier']},
          'activation_function' : {'values' : ['sigmoid', 'tanh', 'relu']}
      }
      
}
sweep_id = wandb.sweep(sweep_config, entity="cs20m040", project="Back_Propagation")

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors
import pandas as pd
import cmath
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, mean_squared_error, log_loss
from tqdm import  tqdm_notebook
from tqdm.notebook import tqdm
from sklearn.preprocessing import OneHotEncoder
from keras.datasets import fashion_mnist
from keras.utils.np_utils import to_categorical

def dataload():
  labels = ['T-shirt/top', 'Trouser', 'Pullover', 'Dress', 'Coat',
                'Sandal', 'Shirt', 'Sneaker', 'Bag', 'Ankle boot']

  (X_train, Y_train), (X_val, Y_val) = fashion_mnist.load_data()

  # reshape dataset to have a single channel
  X_train = X_train.reshape(X_train.shape[0],  1, X_train.shape[1] * X_train.shape[2])
  X_val = X_val.reshape(X_val.shape[0],  1, X_val.shape[1] * X_val.shape[2])

  # Convert from integers to floats
  X_train = X_train.astype('float32')
  X_val = X_val.astype('float32')

  # scale the values between 0 and 1 for both training and testing set
  X_train = X_train / 255.0
  X_val = X_val / 255.0

  enc = OneHotEncoder()
  # 0 -> (1, 0, 0, 0), 1 -> (0, 1, 0, 0), 2 -> (0, 0, 1, 0), 3 -> (0, 0, 0, 1)
  y_OH_train = enc.fit_transform(np.expand_dims(Y_train,1)).toarray()
  y_OH_val = enc.fit_transform(np.expand_dims(Y_val,1)).toarray()

  return X_train, Y_train, X_val, Y_val, y_OH_train, y_OH_val

class BackPropagation:

    #constructor of backpropagation class
    def __init__(self, input_size, output_size=1, init_method = 'random', activation_function = 'sigmoid', leaky_slope = 0.1, hidden_layers=[2], sizes=[32]):
      self.x=input_size
      self.y=output_size
      self.h=len(hidden_layers)
      self.sizes=[self.x] + hidden_layers + [self.y]
      self.init_method = init_method
      self.activation_function = activation_function
      self.leaky_slope = leaky_slope
      self.W={}
      self.B={}

      np.random.seed(0)
      
      #Random Initialization
      if init_method == "random":
        for i in range(self.h+1):
          self.W[i+1] = np.random.randn(self.sizes[i], self.sizes[i+1])
          self.B[i+1] = np.random.randn(self.sizes[i+1])

      #Xavier Initialization
      elif init_method == "xavier":
        for i in range(self.h+1):
          self.W[i+1] = np.random.randn(self.sizes[i], self.sizes[i+1]) * np.sqrt(1 / self.sizes[i-1])
          self.B[i+1] = np.random.randn(self.sizes[i+1])

      for i in range(self.h+1):
        self.W[i+1]=np.random.randn(self.sizes[i], self.sizes[i+1])
        self.B[i+1]=np.zeros((1, self.sizes[i+1]))




    #forward activation function
    def forward_activation(self, X):
      if self.activation_function == "sigmoid":
        return 1.0/(1.0 + np.exp(-X))
      elif self.activation_function == "tanh":
        return np.tanh(X)
      elif self.activation_function == "relu":
        return np.maximum(0, X)


    #compute gradient of the activation function
    def grad_activation(self, X):
      if self.activation_function == "sigmoid":
        return X * (1 - X)
      elif self.activation_function == "tanh":
        return (1-np.square(np.tanh(X)))
      elif self.activation_function == "relu":
        return (1.0*(X>0))
    
    
    #compute perceptron
    def perceptron(self, x, w, b):
      return np.dot(x, w)+ b


    #compute sigmoid
    def sigmoid(self, x):
      return (1.0/(1.0 + np.exp(-x)))


    #compute gradient of the sigmoid
    def grad_sigmoid(self, x):
      return x * (1-x)


    #compute softmax 
    def softmax(self, y):
      exps=np.exp(y)
      return np.exp(y)/np.sum(exps)


    #run forward pass in the neural network
    def forward_pass(self, x):
      self.A={}
      self.H={}
      self.H[0]= x
      
      for i in range(self.h+1):
        self.A[i+1]=np.matmul(self.H[i], self.W[i+1]) + self.B[i+1]
        self.H[i+1]=self.forward_activation(self.A[i+1])
      self.H[self.h+1]=self.softmax(self.A[self.h+1])
      return self.H[self.h+1]




    #compute gradients 
    def grad(self, x, y):
      L=self.h+1

      self.forward_pass(x)

      self.dW={}
      self.dB={}
      self.dA={}
      self.dH={}

      self.dA[L]=(self.H[L]-y)
      for k in range(L, 0, -1):
        self.dW[k]=np.matmul(self.H[k-1].T, self.dA[k])
        self.dB[k]=self.dA[k]
        self.dH[k-1]=np.matmul(self.dA[k], self.W[k].T)
        self.dA[k-1]=np.multiply(self.dH[k-1], self.grad_activation(self.H[k-1]))


    #predict output on the basis of data
    def predict(self, X):
      preds=[]
      for x in X:
        preds.append(self.forward_pass(x)) 
      return np.array(preds).squeeze()


    #compute cross entropy
    def cross_entropy(self,label,pred):
      yl=np.multiply(pred,label)
      yl=yl[yl!=0]
      yl=-np.log(yl)
      yl=np.mean(yl)
      return yl


    #trains the backpropagation model
    def fit(self, X, Y, epochs=1, lr=0.001, initialize=True, display_loss=False, opt_algo='adam', l2_norm=False, weight_decay=0.8, batch_size=128, gamma=0.9, beta=0.9, beta1=0.9, beta2=0.999, epsi=1e-8):
    
      X, X1, Y, Y1 = train_test_split(X, Y, test_size=0.1, random_state=1)
      accuracy, val_accuracy, loss, val_loss= {}, {}, {}, {}
      cross_entrophy_loss, cross_val_loss = {}, {}



      if initialize:
        for i in range(self.h+1):
          self.W[i+1]=np.random.randn(self.sizes[i], self.sizes[i+1])
          self.B[i+1]=np.zeros((1, self.sizes[i+1]))
      
      if  display_loss:
        loss={}
      
      vW, vB= {}, {}
      for i in range(self.h+1):
        vW[i+1]=np.zeros((self.sizes[i], self.sizes[i+1]))
        vB[i+1]=np.zeros((1, self.sizes[i+1]))



      for e in tqdm(range(epochs), total=epochs, unit="epoch"):
        m=X.shape[0]
        dW, dB= {}, {}

        
         
        for i in range(self.h+1):
          dW[i+1]=np.zeros((self.sizes[i], self.sizes[i+1]))
          dB[i+1]=np.zeros((1, self.sizes[i+1]))

        # Gradient Descent
        if opt_algo=='gd':
          for x, y in zip(X, Y):
            self.grad(x, y)
            for i in range(self.h+1): 
              if l2_norm:
                dW[i+1]+=self.dW[i+1] + weight_decay * self.W[i+1]
              else:
                dW[i+1]+=self.dW[i+1]
              dB[i+1]+=self.dB[i+1]

            for i in range(self.h+1):
              self.W[i+1]-= lr*dW[i+1]/m
              self.B[i+1]-= lr*dB[i+1]/m


        # Stochastic Gradient Descent
        elif opt_algo=='sgd':
          
          sample_count= 0
          for x, y in zip(X, Y):
            self.grad(x, y)
            sample_count+=1
            for i in range(self.h+1): 
              if l2_norm:
                dW[i+1]+= self.dW[i+1] + weight_decay * self.W[i+1]
              else:
                dW[i+1]+=self.dW[i+1]              
              dB[i+1]+= self.dB[i+1]

            if sample_count % batch_size == 0:
              for i in range(self.h+1): 
                self.W[i+1]-= lr*dW[i+1]/batch_size
                self.B[i+1]-= lr*dB[i+1]/batch_size
              


        # Momentum Based Gradient Descent
        elif opt_algo=='mgd':

          sample_count=0
          for x, y in zip(X, Y):
            self.grad(x, y) 
            for i in range(self.h+1): 
              if l2_norm:
                dW[i+1]+= self.dW[i+1] + weight_decay * self.W[i+1]
              else:
                dW[i+1]+=self.dW[i+1]              
              dB[i+1]+= self.dB[i+1]
            
          sample_count+=1
          if sample_count % batch_size == 0:
            for i in range(self.h+1):
              vW[i+1]= gamma * vW[i+1] + lr*dW[i+1]
              vB[i+1]= gamma * vB[i+1] + lr*dB[i+1]
              self.W[i+1]-= vW[i+1]
              self.B[i+1]-= vB[i+1]
          

        # Nestrov Accelerated Gradient Descent
        elif opt_algo=='nag':

          sample_count=0
          for x, y in zip(X, Y):
            self.grad(x, y)
            sample_count+=1
            for i in range(self.h+1): 
              if l2_norm:
                dW[i+1]+= self.dW[i+1] + weight_decay * self.W[i+1]
              else:
                dW[i+1]+=self.dW[i+1]              
              dB[i+1]+= self.dB[i+1]

            tW, tB= {}, {}
            for i in range(self.h+1):
              tW[i+1]= self.W[i+1] - gamma * vW[i+1]
              tB[i+1]= self.B[i+1] - gamma * vB[i+1]
              self.W[i+1]= tW[i+1]
              self.B[i+1]= tB[i+1]

            self.grad(x, y)
            for i in range(self.h+1):
              self.W[i+1]= (tW[i+1] - lr * self.dW[i+1]) 
              self.B[i+1]= (tB[i+1] - lr * self.dB[i+1])

            for i in range(self.h+1):
              vW[i+1]= (gamma * vW[i+1] + lr * self.dW[i+1])
              vB[i+1]= (gamma * vB[i+1] + lr * self.dB[i+1]) 
              self.W[i+1]= tW[i+1] - vW[i+1]
              self.B[i+1]= tB[i+1] - vB[i+1] 




        # RMSProp Gradient Descent
        elif opt_algo=='rmsprop':

          sample_count=0
          for x, y in zip(X, Y):
            self.grad(x, y)
            sample_count+=1
            
            for i in range(self.h+1): 
              dW[i+1]+=self.dW[i+1]
              dB[i+1]+=self.dB[i+1]

            if sample_count % batch_size == 0:

              for i in range(self.h+1):
                vW[i+1]= beta * vW[i+1] + (1-beta) * np.power(dW[i+1], 2)
                vB[i+1]= beta * vB[i+1] + (1-beta) * np.power(dB[i+1], 2)
              
              for i in range(self.h+1):
                self.W[i+1]-= (lr/np.sqrt(vW[i+1] + epsi)) * dW[i+1]
                self.B[i+1]-= (lr/np.sqrt(vB[i+1] + epsi)) * dB[i+1]




        # Adam Gradient Descent
        elif opt_algo=='adam':

          sample_count=0
          for x, y in zip(X, Y):
            self.grad(x, y)
            sample_count+=1
          
            for i in range(self.h+1): 
              dW[i+1]+=self.dW[i+1]
              dB[i+1]+=self.dB[i+1]
              
            if sample_count % batch_size == 0:
              mW, mB= {}, {}
              for i in range(self.h+1):
                mW[i+1]= np.zeros(dW[i+1].shape)
                mB[i+1]= np.zeros(dB[i+1].shape)
                mW[i+1]= beta1 * mW[i+1] + (1-beta1) * dW[i+1]
                mB[i+1]= beta1 * mB[i+1] + (1-beta1) * dB[i+1]   

                vW[i+1]= beta2 * vW[i+1] + (1-beta2) * np.power(dW[i+1], 2.0)
                vB[i+1]= beta2 * vB[i+1] + (1-beta2) * np.power(dB[i+1], 2.0)
          
                mW[i+1]= (mW[i+1]/(1.0 - np.power(beta1 , sample_count)))
                mB[i+1]= (mB[i+1]/(1.0 - np.power(beta1 , sample_count)))
                vW[i+1]= (vW[i+1]/(1.0 - np.power(beta2 , sample_count))) 
                vB[i+1]= (vB[i+1]/(1.0 - np.power(beta2 , sample_count))) 
                  
                self.W[i+1] -= (lr / (np.sqrt(vW[i+1] + epsi))) * mW[i+1]
                self.B[i+1] -= (lr / (np.sqrt(vB[i+1] + epsi))) * mB[i+1]




        # Nadam Gradient Descent
        elif opt_algo=='nadam':
          sample_count=0
          for x, y in zip(X, Y):
            self.grad(x, y)
            sample_count+=1
            for i in range(self.h+1): 
              if l2_norm:
                dW[i+1]+= self.dW[i+1] + weight_decay * self.W[i+1]
              else:
                dW[i+1]+=self.dW[i+1]              
              dB[i+1]+= self.dB[i+1]


            if sample_count % batch_size == 0:
              mW, mB= {}, {}
              for i in range(self.h+1): 
                mW[i+1]= np.zeros(dW[i+1].shape)
                mB[i+1]= np.zeros(dB[i+1].shape)
                mW[i+1]= beta1 * mW[i+1] + (1-beta1) * dW[i+1]
                mB[i+1]= beta1 * mB[i+1] + (1-beta1) * dB[i+1]

              #for i in range(self.h+1):
                vW[i+1]= beta2 * vW[i+1] + (1-beta2) * np.power(dW[i+1], 2)
                vB[i+1]= beta2 * vB[i+1] + (1-beta2) * np.power(dB[i+1], 2)
              
              #for i in range(self.h+1):
                mW[i+1]= mW[i+1] / (1.0 - np.power(beta1 , sample_count))
                mB[i+1]= mB[i+1] / (1.0 - np.power(beta1 , sample_count))
                vW[i+1]= vW[i+1] / (1.0 - np.power(beta2 , sample_count))
                vB[i+1]= vB[i+1] / (1.0 - np.power(beta2 , sample_count))

                xW, xB= {}, {}
                xW[i+1]= beta1 * mW[i+1] + (1-beta1) * dW[i+1] / (1.0 - np.power(beta1, sample_count))
                xB[i+1]= beta1 * mB[i+1] + (1-beta1) * dB[i+1] / (1.0 - np.power(beta1, sample_count))
                self.W[i+1]-= (lr  / (np.sqrt(vW[i+1] + epsi))) * xW[i+1]
                self.B[i+1]-= (lr / (np.sqrt(vB[i+1] + epsi))) * xB[i+1] 
                

       

        # Calculating Loss and Accuracy
        y_preds=self.predict(X)
        y_val_preds=self.predict(X1)
        loss[e]=mean_squared_error(y_preds, Y)
        val_loss[e]=mean_squared_error(y_val_preds, Y1)
        cross_entrophy_loss[e]=self.cross_entropy(y_preds, Y)
        cross_val_loss[e]=self.cross_entropy(y_val_preds, Y1)
        accuracy[e]= accuracy_score(np.argmax(y_preds, axis=1), np.argmax(Y, axis=1))
        val_accuracy[e]= accuracy_score(np.argmax(y_val_preds, axis=1), np.argmax(Y1, axis=1))
        wandb.log({ 'Epoch': e, 'Mean_Squared_loss': loss[e], 'Mean_Squared_Val_loss': val_loss[e],'Cross_Entrophy_Loss': cross_entrophy_loss[e], 'Cross_Entropy_Val_loss': cross_val_loss[e], 'Accuracy': accuracy[e], 'Val_accuracy': val_accuracy[e]})


      # Plotting Loss
      if display_loss:
        plt.plot(np.array(list(loss.values())).astype(float))
        plt.xlabel("Epoch")
        plt.ylabel("Cross Entropy Loss")
        plt.show()

def train():
  config_defaults = {
      'epochs' : 15,
      'batch_size' : 128,
      'weight_decay' : 0.0005,
      'learning_rate' : 0.01,
      'activation_function' : 'relu',
      'dropout' : 0.5,
      'momentum' : 0.9,
      'seed' : 42,
      'hidden_layers' : 4,
      'opt_algo' : 'nadam',
      'sizes' : 64,
      'init_method' : 'random',
      'weight_decay' : 0.5
      }
  wandb.init(config=config_defaults)
  config = wandb.config
  hl= [config.sizes for h in range(config.hidden_layers)]
  
  X_train, Y_train, X_val, Y_val, y_OH_train, y_OH_val = dataload()

  back_pro = BackPropagation(X_train.shape[2], y_OH_train.shape[1], init_method=config.init_method, activation_function = config.activation_function, hidden_layers=hl )
  back_pro.fit(X_train, y_OH_train, initialize=False, display_loss=True, opt_algo = config.opt_algo , l2_norm=False, epochs = config.epochs, lr=config.learning_rate, weight_decay=config.weight_decay, batch_size=config.batch_size)
  
  
  preds=back_pro.predict(X_val)
  preds=np.argmax(preds, 1)
  test=np.argmax(y_OH_val, 1)
  accuracy = accuracy_score(test, preds)
  print(accuracy)
  wandb.log({ "accuracy" : accuracy})

wandb.agent(sweep_id,function=train)

#wandb.log({"Confusion_matrix" : wandb.plot.confusion_matrix()})