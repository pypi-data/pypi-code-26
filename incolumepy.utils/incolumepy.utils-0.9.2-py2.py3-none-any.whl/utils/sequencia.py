#coding: utf-8
from math import sqrt
from deprecated import deprecated


@deprecated(version='0.9.2', reason="Replaced for incolumepy.sequencias")
class Sequencia:

    class Fibonacci:
        @deprecated(version='0.9.2', reason="Replaced for incolumepy.sequencias")
        def __init__(self):
            self.seq = [1, 1]

        @deprecated(version='0.9.2', reason="Replaced for incolumepy.sequencias")
        def __next__(self):
            self.seq.append(sum(self.seq))
            return self.seq.pop(0)

        @deprecated(version='0.9.2', reason="Replaced for incolumepy.sequencias")
        def __iter__(self):
            return Sequencia.Fibonacci()

    class Naturais:
        @deprecated(version='0.9.2', reason="Replaced for incolumepy.sequencias")
        def __init__(self):
            self.lista = [0]

        @deprecated(version='0.9.2', reason="Replaced for incolumepy.sequencias")
        def __next__(self):
            self.lista.append(self.lista[0] + 1)
            return self.lista.pop(0)

        @deprecated(version='0.9.2', reason="Replaced for incolumepy.sequencias")
        def __iter__(self):
            return Sequencia.Naturais()


    class Pares:
        @deprecated(version='0.9.2', reason="Replaced for incolumepy.sequencias")
        def __init__(self):
            self.lista = [2]

        @deprecated(version='0.9.2', reason="Replaced for incolumepy.sequencias")
        def __next__(self):
            self.lista.append(self.lista[0] + 2)
            return self.lista.pop(0)

        @deprecated(version='0.9.2', reason="Replaced for incolumepy.sequencias")
        def __iter__(self):
            return Sequencia.Pares()

        @deprecated(version='0.9.2', reason="Replaced for incolumepy.sequencias")
        def ispar(self, num):
            return num % 2 == 0

    class Impares:
        @deprecated(version='0.9.2', reason="Replaced for incolumepy.sequencias")
        def __init__(self):
            self.lista = [1]

        @deprecated(version='0.9.2', reason="Replaced for incolumepy.sequencias")
        def __next__(self):
            self.lista.append(self.lista[0] + 2)
            return self.lista.pop(0)

        @deprecated(version='0.9.2', reason="Replaced for incolumepy.sequencias")
        def __iter__(self):
            return Sequencia.Impares()

        @deprecated(version='0.9.2', reason="Replaced for incolumepy.sequencias")
        def isimpar(self, num):
            return num % 2 == 1

    class Primos:
        '''
        Números primos são os números naturais maiores que 1 e têm apenas dois divisores diferentes: o 1 e ele mesmo.
        '''
        primos = []

        @deprecated(version='0.9.2', reason="Replaced for incolumepy.sequencias")
        def __init__(self):
            self.primos = [2, 3, 5, 7]
            self.seq = Sequencia.Naturais()

        @deprecated(version='0.9.2', reason="Replaced for incolumepy.sequencias")
        def __next__(self):
            while 1:
                value = self.seq.__next__()
                if self.isprimo(value):
                    self.primos.append(value)
                    return self.primos[-1]

        @deprecated(version='0.9.2', reason="Replaced for incolumepy.sequencias")
        def __iter__(self):
            return Sequencia.Primos()

        @deprecated(version='0.9.2', reason="Replaced for incolumepy.sequencias")
        def isprimo(self, numero):

            if numero in self.primos:
                return True

            if numero <= 1:
                return False

            if Sequencia.Pares().ispar(numero):
                return False

            for i in range(3, numero + 1, 2):

                if (i != numero):
                    if (numero % i == 0):
                        return False
                    if  i > sqrt(numero):
                        continue
                else:
                    self.primos.append(numero)
                    return True



def Main():
    print('\nPrimos')
    a = Sequencia.Primos()
    for i in range(1, 1051):
        print(i, a.__next__())



if __name__ == '__main__':
    Main()
