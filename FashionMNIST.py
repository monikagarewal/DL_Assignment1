# -*- coding: utf-8 -*-
"""Wandb.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1vA1Quk4341ZfthU1IlClhXlb18qcCQH4
"""

!pip install wandb -qqq
import wandb
wandb.init(project="Back_Propagation", entity="cs20m040")
!wandb login fb3bb8a505ba908b667b747ed68e4b154b2f6fc5

from keras.datasets import fashion_mnist

labels = ['T-shirt/top', 'Trouser', 'Pullover', 'Dress', 'Coat',
                'Sandal', 'Shirt', 'Sneaker', 'Bag', 'Ankle boot']

def load():
  # download and load the dataset
  (x_train, y_train), (x_test, y_test) = fashion_mnist.load_data()
  x_train, x_val = x_train[:5000], x_train[5000:]
  y_train, y_val = y_train[:5000], y_train[5000:]

  return {
      'x_train': x_train,
      'y_train': y_train,
      'x_val': x_val,
      'y_val': y_val,
      'x_test': x_test,
      'y_test': y_test,
  }

def logImages():
  dataset = load()
  train_images = dataset['x_train']
  train_labels = dataset['y_train']
  set_images = []
  set_labels = []
  for i in range(len(train_images)):
    if len(set_labels) == 10:
      break
    if labels[train_labels[i]] not in set_labels:
      set_images.append(train_images[i])
      set_labels.append(labels[train_labels[i]])

  wandb.log({"Fasion_images": [wandb.Image(img, caption=caption) for img, caption in zip(set_images, set_labels)]})

logImages()
