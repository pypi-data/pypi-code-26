#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# pyelectrica.py
#
# Autor: Isai Aragón Parada
#

"""
Modulo Python con funciones útiles para resolver problemas específicos
en la Ingeniería Eléctrica.
"""

__author__ = "Isai Aragón Parada"
__copyright__ = "Copyright 2018, Isai Aragón"
__credits__ = "Isai Aragón Parada"
__license__ = "MIT"
__version__ = "1.0.2"
__maintainer__ = "Isai Aragón Parada"
__email__ = "isaix25@gmail.com"
__status__ = "En constante desarrollo"

#-----------------------------------------------------------------------------

# Se importan los modulos necesarios
import matplotlib.pyplot as plt
from numpy import linspace, arange, pi, cos, sin, exp, array, sqrt
from numpy.linalg import solve
from scipy import signal

#-----------------------------------------------------------------------------

# Función para calcular la Ley de Ohm, en base al parámetro con incognita '?'.


def leyOhm(**param):
    """
    Función para calcular la Ley de Ohm, en base al parámetro
    con incognita '?'.
    Ejemplo:
    leyOhm(V='?', I=3, R=4)
    """

    if param['V'] == '?':
        print('V =',
              round(float(param['I'] * param['R']), 2), 'V')

    elif param['I'] == '?':
        print('I =',
              round(float(param['V'] / param['R']), 2), 'A')

    elif param['R'] == '?':
        print('R =',
              round(float(param['V'] / param['I']), 2), 'Ω')

    else:
        print('¡No hay nada que calcular!')
        print('''         (#_#)''')
        print('Si quieres que calcule algo,')
        print('tienes que poner la incognita \'?\' ')

#-----------------------------------------------------------------------------

# Función para calcular los diagramas de bode. Versión Script.


def bode(num, den):
    """
    Función que genera los diagramas de Bode para una función  de
    transferencia, indicada por su numerador (num) y denominador(den).
    """

    # Se determina el tamaño de la gráfica
    import pylab
    pylab.rcParams['figure.figsize'] = (9, 6.5)

    # Se declara la función de transferencia, frecuencia (w), magnitud (mag)
    # y la fase.
    sistema = signal.TransferFunction(num, den)
    w, mag, fase = signal.bode(sistema)

    # Se generan las gráficas de la lo diagramas de Bode.
    # Diagrama de Amplitud
    plt.subplot(2, 1, 1)
    plt.semilogx(w, mag)
    plt.title('Diagramas de Bode')
    plt.ylabel('Amplitud $(dB)$')
    plt.grid(True, which='both', axis='both')

    # Diagrama de Fase
    plt.subplot(2, 1, 2)
    plt.semilogx(w, fase)
    plt.ylabel('Fase $(°)$')
    plt.xlabel('$ \omega \ (rad/seg) $')
    plt.grid(which='both', axis='both')

    # Se muestran los diagrmas en pantalla
    plt.show()

#-----------------------------------------------------------------------------

# Función para calcular los diagramas de Bode. Versión Jupyter Notebook.


def bodeNb(num, den):
    """
    Función que genera los diagramas de Bode para una función  de
    transferencia, indicada por su numerador (num) y denominador(den).
    """

    # Se determina el tamaño de la gráfica
    import pylab
    pylab.rcParams['figure.figsize'] = (9, 6.5)

    # Se declara la función de transferencia, frecuencia (w), magnitud (mag)
    # y la fase.
    sistema = signal.TransferFunction(num, den)
    w, mag, fase = signal.bode(sistema)

    # Se generan las gráficas de la lo diagramas de Bode.
    # Diagrama de Amplitud
    plt.figure()
    plt.semilogx(w, mag)
    plt.title('Diagramas de Bode')
    plt.ylabel('Amplitud $(dB)$')
    plt.grid(True, which='both', axis='both')

    # Diagrama de Fase
    plt.figure()
    plt.semilogx(w, fase)
    plt.ylabel('Fase $(°)$')
    plt.xlabel('$ \omega \ (rad/seg) $')
    plt.grid(which='both', axis='both')

    # Se muestran los diagrmas en pantalla
    plt.show()

#-----------------------------------------------------------------------------

# Función para generar la respuesta escalón de una función de transferencia.


def escalon(num, den):
    """
    Función escalón, para generar la respuesta escalón en base a una
    función de transferencia.

    num = valores en formato de lista, que contiene lo valores del
    númerador de la fución de transferencia.

    den = valores en formato de lista, que contiene los valores del
    denominador de la función de transferencia.
    """

    # Se declara la función de transferencia, se genera el tiempo (t),  y
    # la respuesta escalon y(t).
    sistema = signal.TransferFunction(num, den)
    t, y = signal.step(sistema)

    # Se declara la gráfica la respuesta escalón .
    plt.plot(t, y, 'r')
    plt.title('Respuesta escalón')
    plt.xlabel('Tiempo $(s)$')
    plt.ylabel('Amplitud')
    plt.grid()

    # Se imprime en pantalla la gráfica de la respuesta escalón.
    plt.show()

#-----------------------------------------------------------------------------

# Función para resolver un sistema de ecuaciones en forma matricial.
# Generadas por el analisis nodal de un circuito eléctrico.


def vNodos(A, B):
    """
    Función vNodos, que resuelve un sistema de ecuaciones en forma
    matricial y entrega los correspondientes voltajes de nodo en base
    al sistema de ecuaciones del circuito.
    A = lista que define la matriz de coeficiente.
    B = lista que define la matriz del vector solución.
    """

    #mA = array(A)
    #mB = array(B)
    V = solve(A, B)

    print('Los voltajes de nodo del circuito son:\n')

    # Se genera una iteración sobre cada uno de los valores de la matriz V.
    # Para imprimir la designación de cada voltaje con su respectivo valor.

    num = 0
    for v in V:
        num += 1
        print('v' + str(num), '=', round(v[0], 2), 'Volts')

# Se genera función que imprime las corrientes de lazo en forma de lista
# para que puedan ser manipulados.


def vNodosV(A, B):
    """
    Función vNodos, que resuelve un sistema de ecuaciones en forma
    matricial y entrega los correspondientes voltajes de nodo en base
    al sistema de ecuaciones del circuito.
    A = lista que define la matriz de coeficiente.
    B = lista que define la matriz del vector solución.
    """

    #mA = array(A)
    #mB = array(B)
    V = solve(A, B)

#-----------------------------------------------------------------------------


# Función para resolver un sistema de ecuaciones en forma matricial.
# Generadas por el analisis nodal de un circuito eléctrico.


def iLazos(A, B):
    """
    Función iLazos, que resuelve un sistema de ecuaciones en forma
    matricial y entrega las correspondientes corrientes de lazo en base
    al sistema de ecuaciones del circuito.
    A = lista que define la matriz de coeficiente.
    B = lista que define la matriz del vector solución.
    """

    #mA = array(A)
    #mB = array(B)
    I = solve(A, B)

    print('Las corrientes de lazo del circuito son:\n')

    # Se genera una iteración sobre cada uno de los valores de la matriz I.
    # Para imprimir la designación de cada corriente con su respectivo valor.

    num = 0
    for i in I:
        num += 1
        print('i' + str(num), '=', round(i[0], 2), 'Amperes')

# Se genera función que imprime las corrientes de lazo en forma de lista
# para que puedan ser manipulados.


def iLazosV(A, B):
    """
    Función iLazosF (Entrega lista de valores), que resuelve un sistema
    de ecuaciones en forma matricial y entrega las correspondientes
    corrientes de lazo en base al sistema de ecuaciones del circuito.
    A = lista que define la matriz de coeficiente.
    B = lista que define la matriz del vector solución.
    """

    #mA = array(A)
    #mB = array(B)
    return solve(A, B)

#-----------------------------------------------------------------------------


# Función para encontrar la magnitud de la fuerza inducida en un alambre, te-
# niendo como datos la corriente(i), la longitud (l) y la densidad de flujo de
# campo.


def mLineal_CD(Vb=120, R=0.5, l=1, B=0.5):
    """
    Función \"mLineal_CD\", util para calcular el comportamiento de una
    máquina lineal CD en base a los parámetros declarados.

    mLineal_CD(Vb, R, l, B)

    Vb = Voltaje de la batería
    R = Resistencia del diagrama de la máquina lineal CD
    l = longitud del conductor en el campo magnético
    B =  Vector de densidad de flujo magnético
    """

    # Se declara el rango de fuerzas a aplicar
    F = linspace(0, 50, num=50)

    # Se Calcula la corriente en el motor
    i = F / (l * B)

    # Se calcula el voltaje inducido
    eind = Vb - (i * R)

    # Se calcula la velocidad de la barra
    Vel = eind / (l * B)

    # Se grafica la velocidad en función de la fuerza aplicada
    plt.plot(F, Vel, 'b', label='Velocidad')
    plt.plot(F, i, 'r', label='Corriente')
    plt.plot(F, eind, 'g', label='Voltaje inducido')

    plt.title('Comportamiento de la maquina lineal CD')
    plt.xlabel('Fuerza (N)')
    plt.ylabel('Velocidad barra (m/s) / Corriente (A) / $e_{ind}$ (V)')
    plt.legend(loc='best')
    plt.grid()

    plt.show()


#-----------------------------------------------------------------------------


# Función "compCA_GenSinc" que genera una la gráfica de la componente AC
# de la corriente de falla de un generador síncrono.


def compCA_GenSinc(Sbase=(100 * 10**6), Vbase=(13.8 * 10**3), Xs=1.0,
                   X1p=0.25, X2p=0.12, T1p=1.10, T2p=0.04):
    """
    Función \"compCA_GenSinc\" para calcular la componente CA de la
    corriente de falla de un generador síncrono en base a los
    parámetros ingresados.

    Ejemplo:
    compCA_GenSinc(Sbase, Vbase, Xs, X1p, X2p, T1p, T2p)

    Donde:
    Sbase = Potencia aparente del generador síncrono
    Vbase = Voltaje base del generador síncrono
    Xs = Reactancia síncrona del generador síncrono
    X1p = Reactancia transitoria
    X2p = Reactancia subtrancitoria
    T1p = Constante de tiempo de la corriente transitoria
    T2p = Constante de tiempo de la corriente subtrancitoria
    """

    # Se determina el tamaño de la gráfica
    import pylab
    pylab.rcParams['figure.figsize'] = (10, 6.18)

    # Se calcula la componente ac de la corriente
    t = linspace(0.0, 5.0, num=155)

    Ibase = Sbase / (sqrt(3) * Vbase)

    I2p = (1.0 / X2p) * Ibase
    I1p = (1.0 / X1p) * Ibase
    Iss = (1.0 / Xs) * Ibase

    It = (I2p - I1p) * exp(-t / T2p) + (I1p - Iss) * exp(-t / T1p) + Iss

    Isen = It * sin(2 * pi * 60 * t)

    # Se grafica la componente ac de la corriente
    plt.plot(t, It, 'r')
    plt.plot(t, Isen, 'b')
    plt.plot(t, -It, 'r')

    plt.title('Componente CA de corriente de falla en generador síncrono')
    plt.xlabel('tiempo (s)')
    plt.ylabel('Corriente de corto circuito (A)')

    plt.grid()

    plt.show()

#-----------------------------------------------------------------------------


# Función "par_vel" que genera una la gráfica de la curva Par-Velocidad
# de un motor de inducción.


def par_vel(Vn=460, Polos=4, f=60, R1=0.641, X1=1.106,
            R2=0.332, X2=0.464, Xm=26.3):
    """
    Función \"par_vel\" para calcular y generar la gráfica de la curva
    Par-Velocidad de un motor de inducción con rotor devanado y/o
    rotor jaula de ardilla.

    Ejemplo:
    par_vel(Vn, Polos, f, R1, X1, R2, X2, Xm)

    Donde:
    Vn = Voltaje nominal del motor
    Polos = Número de polos del motor
    f = Frecuencia de operación del motor
    R1 = Resistencia del estator
    X1 = Reactancia del estator
    R2 = Resistencia del rotor
    X2 = Reactancia del rotor
    Xm = Reactancia de magnetización
    """

    # Se determina el tamaño de la gráfica
    import pylab
    pylab.rcParams['figure.figsize'] = (10, 6.18)

    # Se preparan las variables para el cálculo
    Vfase = Vn / sqrt(3)

    ns = 120 * f / Polos
    ws = ns * (2 * pi / 1) * (1 / 60)

    s = arange(0.001, 1.0, 0.001)

    # Se calcula el voltaje y la impedancia de Thevenin
    Vth = Vfase * (Xm / sqrt(R1**2 + (X1 + Xm)**2))
    Zth = ((1j * Xm) * (R1 + 1j * X1)) / (R1 + 1j * (X1 + Xm))
    Rth = Zth.real
    Xth = Zth.imag

    # Se calcula la característica par-velocidad
    nm = (1 - s) * ns

    # Se calcula el Par para la resistencia original del rotor
    t_ind = (3 * Vth**2 * R2 / s) / (
        ws * ((Rth + R2 / s)**2 + (Xth + X2)**2))

    # Se calcula el Par para el doble de la resistencia del rotor
    t_ind2 = (3 * Vth**2 * (2 * R2) / s) / (
        ws * ((Rth + (2 * R2) / s)**2 + (Xth + X2)**2))

    # Se generan las curvas Par-Velocidad
    plt.plot(nm, t_ind, 'b', label='$R_2 \ $ Original')
    plt.plot(nm, t_ind2, 'r-.', label='$R_2 \ $ Duplicada')

    plt.title('Curva Par-Velocidad del motor de inducción')
    plt.xlabel('$n_m$, $r/min$')
    plt.ylabel('$\\tau_{ind} $, $N*M$')
    plt.legend()
    plt.grid()

    plt.show()

#-----------------------------------------------------------------------------


if __name__ == "__main__":
    print('Este es el modulo \"PyElectrica\" para Python.')
    print('Útil en la solución de problemas de Ingeniería Eléctrica.')
    input('Presiona <Enter> para salir.')
