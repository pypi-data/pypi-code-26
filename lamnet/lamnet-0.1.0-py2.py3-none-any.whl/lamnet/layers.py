"""
Nnet is made up of layers
Each layer need to pass its input forward
and propagate gradients backward. For example, the architecture is:
inputs -> linear -> Tanh -> linear -> output
"""

import numpy as np
from lamnet.tensor import Tensor
from typing import Dict, Callable

class Layer:
    def __init__(self) -> None:
        self.params : Dict[str, Tensor] = {}
        self.grads : Dict[str, Tensor] = {}

    def forward(self, inputs: Tensor) -> Tensor:
        """
        just produce outputs from inputs
        """
        raise NotImplementedError

    def backward(self, grad: Tensor) -> Tensor:
        raise NotImplementedError


class Linear(Layer):
    """
    computes output = input @ w + b
    """
    def __init__(self, input_size: int, output_size: int) -> None:
        # inputs: (bs, input_size)
        # outputs: (bs, output_size)
        super().__init__()
        self.params["w"] = np.random.randn(input_size, output_size)
        self.params["b"] = np.random.randn(output_size)

    def forward(self, inputs: Tensor) -> Tensor:
        """
        outputs = inputs @ w + b
        """
        self.inputs = inputs
        return inputs @ self.params["w"] + self.params["b"]

    def backward(self, grad: Tensor) -> Tensor:
        """
        if y = f(x) and x = a * b + c
        then dy/da = f'(x) * b, dy/db = f'(x) * a, dy/dc = f'(x)
        
        if y = f(x) and x = a @ b + c
        then dy/da = f'(x) @ b.T, dy/db = a.T @ f'(x), dy/dc = f'(x)
        """
        self.grads["b"] = np.sum(grad, axis=0)
        self.grads["w"] = self.inputs.T @ grad
        return grad @ self.params["w"].T

F = Callable[[Tensor], Tensor]

class Activation(Layer):
    """
    An activation layer just applies a function elementwise to its inputs
    """
    def __init__(self, f: F, f_prime: F) -> None:
        super().__init__()
        self.f = f
        self.f_prime = f_prime

    def forward(self, inputs: Tensor) -> Tensor:
        self.inputs = inputs
        return self.f(inputs)

    def backward(self, grad: Tensor) -> Tensor:
        """
        if y = f(x) and x = g(z)
        then dy/dz = f'(x) * g'(z)
        """
        return self.f_prime(self.inputs) * grad

def tanh(x: Tensor) -> Tensor:
    return np.tanh(x)

def tanh_prime(x: Tensor) -> Tensor:
    y = tanh(x)
    return 1 - y ** 2

class Tanh(Activation):
    def __init__(self):
        super().__init__(tanh, tanh_prime)

def sigmoid(x: Tensor) -> Tensor:
    return 1/(1 + np.exp(-x))

def sigmoid_prime(x: Tensor) -> Tensor:
    y = sigmoid(x)
    return y*(1-y)

class Sigmoid(Activation):
    def __init__(self):
        super().__init__(sigmoid, sigmoid_prime)

### my updated activations ###
def relu(x: Tensor) -> Tensor:
    return np.where(x>0,x,0)

def relu_prime(x: Tensor) -> Tensor:
    return np.where(x>0,1,0)

class Relu(Activation):
    def __init__(self):
        super().__init__(relu, relu_prime)