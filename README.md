# Feed Forward Neural Network

This repository contains a python implementation of Feed Forward Neural Network with Backpropagation and Optimization algorithm along with various parameters from scratch.This model is used to train the network to classify the images of Fashion MNIST Dataset.


# Usage

In BackPropagation_with_Optimzations.py, we have a class called BackPropagation. In this class we're initialising some variables with the help of constructor(__init__) of the class. So, whenever we create the object of the class the class will be initialised. Following are the parameters of the constructor:

1. input_size : An integer represents the number of features of input data.
2. output_size : An integer represents the number of output classes.(we're taking 1 as a default)
3. init_method : A string contains the name of the initialisation method. eg, 'random'(default), 'xavier' , which we use to initialize our network.
4. activation_function : A string represents the name of activation function which we require in forward pass, eg, 'sigmoid'(default), 'tanh' and 'relu'
5. hidden_layers : A list of integers representing the number of hidden layers present between the neurons of the network. eg. 3, 4, 5
6. sizes : A list of integers represents the number of hidden neurons should be between the size of the input layer and the size of the output layer.

In this class, we have various functions:

1. forward_activation() : This function compute the forward activation function for forward pass in the feedforward neural network.
2. grad_activation() : This function compute the gradient for backpropagation.
3. softmax() : This function computes the softmax for the input values.
4. forward_pass() : This function computes all the activation and pre-activation of the neurons within the network.
5. grad() : This function performs the backpropagation within the feedforward neural network.
6. predict() : This function predicts the output on the basis of input data.
7. cross entropy() : This function is use to compute the loss within the network.
8. fit() : Fit function is used to train the model.


# Train the model
In the fit function, we have various parameters.
