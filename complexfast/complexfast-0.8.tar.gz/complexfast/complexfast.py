import numpy as np
import math
import matplotlib.pyplot as plt

class complexfast:
    """
    This is a class for mathematical operations on complex numbers.
     
    Attributes:
        real (float): The real part of complex number.
        img (float): The imaginary part of complex number.
    """

    def __init__(self, real, img):
        """
        This function initialises a complex number.

        This function is called implicitly when the object of this class is created.

        Parameters
        ----------
        real : float
            Real term of the complex number
        img : float
            Imaginary term of complex number

        Returns
        -------
        Complex    

        """
        self.real = real
        self.img = img

    def __repr__(self):
        """
        This function provides a string representation of an object.

        Returns
        -------
        str

        """
        return 'complex({},{})'.format(self.real, self.img)

    def __str__(self):
        """
        This function provides string representation of an object.

        Returns
        -------
        str

        """
        return '{}{operator}{}j'.format(self.real, abs(self.img), operator = '-' if self.img < 0 else '+')

    def __add__(self, other):
        """
        This function emulates the '+' operator.

        Parameters
        ----------
        other : Complex
            Second complex number object

        Returns
        -------
        Complex

        """
        return self.add(other)
        
    def add(self, other):
        """
        This function adds 2 complex numbers.

        Parameters
        ----------
        other : Complex
            Second number

        Returns
        -------
        Complex

        """
        return Complex(float(self.real + other.real), float(self.img + other.img))

    def __sub__(self, other):
        """
        This function emulates '-' operator.

        Parameters
        ----------
        other : Complex
            Second number

        Returns
        -------
        Complex

        """
        return self.sub(other)

    def sub(self, other):
        """
        This function subtracts 2 complex numbers.

        Parameters
        ----------
        other : Complex
            Second number

        Returns
        -------
        Complex

        """
        return Complex(float(self.real - other.real), float(self.img - other.img)) 

    def __mul__(self, other):
        """
        This function emulates '*' operator.

        Parameters
        ----------
        other : Complex
            Second number

        Returns
        -------
        Complex

        """
        return self.mul(other)

    def mul(self, other):
        """
        This function multiplies 2 complex numbers.

        Parameters
        ----------
        other : Complex
            Second number

        Returns
        -------
        Complex

        """
        r1 = self.real
        i1 = self.img
        r2 = other.real
        i2 = other.img

        R = float(r1 * r2 - i1 * i2)
        I = float(r1 * i2 + r2 * i1) 

        return Complex(R, I)

    def __truediv__(self,other):
        """
        This function emulates '/' operator.

        Parameters
        ----------
        other : Complex
            Second number

        Returns
        -------
        Complex

        """
        return self.div(other)

    def div(self, other):
        """
        This function divides 2 complex numbers.

        Parameters
        ----------
        other : Complex
            Second number

        Returns
        -------
        Complex

        """
        r1 = self.real
        i1 = self.img
        r2 = other.real
        i2 = other.img

        R = round(float(r1 * r2 + i1 * i2) / (r2 * r2 + i2 *i2),3)
        I = round(float(r2 * i1 - r1 * i2) / (r2 * r2 + i2 * i2), 3)

        return Complex(R, I)

    def polar(self):
        """
        This function finds polar of a complex number.

        Returns
        -------
        float
            Absolute value of complex number.
        float
            Argument of complex number.

        """
        r = round(float(np.sqrt(self.real ** 2 + self.img ** 2)), 3)
        theta = math.degrees(math.atan(self.img / self.real))

        return r, theta 

    def root(self, n):
        """
        This function finds root of a complex number.

        Parameters
        ----------
        n : int/float
            nth root.

        Returns
        -------
        list
            List of complex numbers.

        """
        r, theta = self.polar()
        r **= (1./n)
        c = []

        for k in range(0, n):
            theta = (math.radians(theta) / n) + ((k * 2 * math.pi) / n)
            r = round(r * math.cos(theta), 3)
            i = round(r * math.sin(theta), 3)
            c.append(Complex(r, i))

        return c

    def power(self, n):
        """
        This function finds power of a complex number.

        Parameters
        ----------
        n : int/float
            nth power.

        Returns
        -------
        Complex
            Power of complex number.

        """ 
        r, theta = self.polar()
        r = r ** n
        theta = math.radians(theta) * n
        R = round(r * math.cos(theta), 3)
        I = round(r * math.sin(theta), 3)

        return Complex(R, I)

    def exp(self, n):
        """
        This function, like power() finds power of a complex number

        Parameters
        ----------
        n : int/float
            nth power.

        Returns
        -------
        Complex
            Power of complex number.

        """
        return self.power(n)

    def conjugate(self):
        """
        This function finds conjugate of a complex number

        Returns
        -------
        Complex
            Conjugate of complex number.

        """
        i = self.img
        if i < 0:
            i = abs(i)
        else:
            i = i * -1

        return Complex(self.real, i)

    def modulus(self):
        """
        This function finds modulus of a complex number

        Returns
        -------
        float
            Modulus of complex number.

        """

        return round(float(np.sqrt(self.real ** 2 + self.img ** 2)), 3)

    def plot(self):

        plt.figure()
        # Set x-axis range
        x_lower = -1 * max(1, abs(self.real))
        x_higher =  max(1, abs(self.real))
        plt.xlim((x_lower-0.5,x_higher+0.5))
        # Set y-axis range
        y_lower = -1 * max(1, abs(self.img))
        y_higher =  max(1, abs(self.img))
        plt.ylim((y_lower-0.5,y_higher+0.5))

        # Draw lines to split quadrants
        plt.plot([0,0],[y_lower-0.5,y_higher+0.5], linewidth=2, color='black' )
        plt.plot([x_lower-0.5,x_higher+0.5],[0,0], linewidth=2, color='black' )
        
        plt.xlabel('Real')
        plt.ylabel('Imaginary')
        plt.title('Geometric representaton of complex number')
        plt.scatter(self.real, self.img)        
        plt.show()
   

# if __name__=="__main__":
    
#     a = Complex(-2,2)
#     b = Complex(1,-1)

#     # Testing different opertaion
#     print("   a: {0},\n   b: {1},\n a+b: {2},\n a-b: {3},\n a*b: {4},\
#     \n Polar: {5},\n root(2): {6},\n power(2): {7},\n exp(2): {8},\n conjugate: {9},\
#     \n modulus: {10},\n a/b: {11}".format(a, b, a+b, a-b, a*b, a.polar(), a.root(2), a.power(2),\
#     a.exp(2), a.conjugate(), a.modulus(), a/b))

#     # a.plot()

#     # def test_add():

#     #     a = Complex(2,-2)
#     #     b = Complex(1,-1)
#     #     add = a + b
#     #     assert add.real == 3
#     #     assert add.img == -3