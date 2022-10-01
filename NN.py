import numpy as np

def segmoid(z):
    return 1.0/(1+np.exp(-z))

class NeuralNetwork():
    def __init__(self) :
        self.weights1=np.random.randn(4,10)
        self.weights2=np.random.randn(11)
    def feedForword(self,*inputs):
        inputs=np.insert(inputs,0,1)
        layer1=segmoid(np.dot(inputs,self.weights1))
        layer1=np.insert(layer1,0,1)
        layer2=segmoid(np.dot(layer1,self.weights2.T))
        return layer2
    def setweights(self,weight1,weight2):
        self.weights1=weight1
        self.weights2=weight2







