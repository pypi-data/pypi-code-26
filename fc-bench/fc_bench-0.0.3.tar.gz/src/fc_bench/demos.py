from __future__ import print_function
import numpy as np
import sys

def Lagrange(X,Y,x):
# LAGRANGE computes the interpolation polynomial in the Lagrange form
# -- y=Lagrange(X,Y,x)
#      returns the interpolate values y as the Lagrange form of the 
#      interpolating polynomial using the points (X(i),Y(j)) so that
#         y(j)=P_n(x(j))
#
  m=len(x);
  y=np.zeros(m)
  for i in np.arange(m): 
    y[i]=LagrangeSca(X,Y,x[i])
  return y


def LagrangeSca(X,Y,x): # x is a scalar, so y=P_n(x) is a scalar
  n=len(X)
  y=0
  for i in np.arange(n):
    L=1
    for j in np.setdiff1d(np.arange(n),i):  
      L=L*(x-X[j])/(X[i]-X[j])
    y=y+Y[i]*L
  return y

def lagint(x, y, xx):
  n = len(x)
  nn = len(xx)
  yy=np.zeros(nn)
  for i in np.arange(nn):
    for k in np.arange(n):
      idx=np.setdiff1d(np.arange(n),k) 
      yy[i] = yy[i]+y[k]*np.prod(xx[i] - x[idx])/np.prod(x[k] - x[idx]);
  return yy

def scipyLagrange(X,Y,x):
  import scipy.interpolate as inter
  return inter.barycentric_interpolate(X,Y,x)

def setLagrange00(N,verbose,**kwargs):
  from fc_bench.bench import bData
  n=N[0] # degree of the interpolating polynomial
  m=N[1] # number of interpolate values
  a=0;b=2*np.pi
  X=np.linspace(a,b,n+1)
  Y=np.cos(X)
  x=a+(b-a)*np.random.rand(m) 
  bDs=[]
  bDs.append(bData('{:>8}'.format('m'),m,'{:5}')) # 1st column
  bDs.append(bData('{:>8}'.format('n'),n,'{:5}')) # 2nd column
  return ((X,Y,x),bDs)

def setLagrange(N,verbose,**kwargs):
  import fc_tools
  a=kwargs.pop('a',0)
  b=kwargs.pop('b',2*np.pi)
  sfun=kwargs.pop('fun','lambda x: np.cos(x)')
  fun=eval(sfun)
  Print=kwargs.get('Print',lambda s: print(s))
  from fc_bench.bench import bData
  n=N[0] # degree of the interpolating polynomial
  m=N[1] # number of interpolate values
  X=np.linspace(a,b,n+1)
  Y=fun(X)
  x=a+(b-a)*np.random.rand(m) 
  Error=lambda y: np.linalg.norm(y-fun(x),np.inf)
  if verbose:
    Print('# Setting inputs of Lagrange polynomial functions: y=LAGRANGE(X,Y,x)')
    Print('# where X is numpy.linspace(a,b,n+1), Y=fun(X) and x is random values on [a,b]')
    Print('#   n is the order of the Lagrange polynomial')
    Print('#   fun function is: %s'%sfun)
    Print('#   [a,b]=[%g,%g]'%(a,b))
    Print('#   X: (n+1,) numpy array')
    Print('#   Y: (n+1,) numpy array')
    Print('#   x: (m,)   numpy array')
    Print('#   Error[i] computed with fun[i] output:')
    Print('#     %s'%fc_tools.others.func2str(Error))
  
  bDs=[]
  bDs.append(bData('{:>5}'.format('m'),m,'{:>5}'))
  bDs.append(bData('{:>5}'.format('n'),n,'{:>5}'))
  return ((X,Y,x,Error),bDs)

def setMatProd00(m,verbose,**kwargs):
  from fc_bench.bench import bData
  X=np.random.randn(m,m)
  Y=np.random.randn(m,m)
  bDs=[bData('{:>8}'.format('m'),m,'{:>8}')]
  return ((X,Y),bDs)

def setMatProd01(m,verbose,**kwargs):
  from fc_bench.bench import bData
  X=np.random.randn(m,m)
  Y=np.random.randn(m,m)
  if verbose:
    print('# 1st input parameter: (m,m) Numpy array')
    print('# 2nd input parameter: (m,m) Numpy array')
  bDs=[bData('{:>8}'.format('m'),m,'{:>8}')]
  return ((X,Y),bDs)

def setMatProd02(m,verbose,**kwargs):
  Print=kwargs.get('Print',lambda s: print(s))
  from fc_bench.bench import bData
  X=np.random.randn(m,m)
  Y=np.random.randn(m,m)
  if verbose:
    Print('# 1st input parameter: (m,m) Numpy array')
    Print('# 2nd input parameter: (m,m) Numpy array')
  bDs=[bData('{:>8}'.format('m'), m, '{:>8}')]
  return ((X,Y),bDs)

def genMat(m,n,dtype,isComplex):
  M=0;
  if isComplex:
    M=1j*np.random.randn(m,n)
  M+=np.random.randn(m,n)
  return M

def setMatProd03(N,verbose,**kwargs):
  assert len(N)==3 or len(N)==1
  Print=kwargs.get('Print',lambda s: print(s))
  ldtype=kwargs.get('ldtype', )
  rdtype=kwargs.get('rdtype', )
  lcomplex=kwargs.get('lcomplex',False)
  rcomplex=kwargs.get('rcomplex',False)
  
  from fc_bench.bench import bData
  if len(N)==1:
    m=n=p=N
  else:
    [m,n,p]=N
    
  X=genMat(m,n,ldtype,lcomplex)
  Y=genMat(n,p,rdtype,rcomplex)
  
  if verbose:
    Print('# 1st input parameter: (m,n) Numpy array [%s]'%str(X.dtype))
    Print('# 2nd input parameter: (n,p) Numpy array [%s]'%str(Y.dtype))
  bDs=[bData('{:>7}'.format('m'), m, '{:>7}')]
  bDs.append(bData('{:>7}'.format('n'), n, '{:>7}'))
  bDs.append(bData('{:>7}'.format('p'), p, '{:>7}'))
  return ((X,Y),bDs)

def bench_Lagrange00():
  import fc_bench
  import numpy as np
  Lfun=[Lagrange,lagint,scipyLagrange]
  n=[5,9,15]; m=[100,500,1000];
  N,M=np.meshgrid(n,m)
  LN=np.vstack((N.flatten(),M.flatten())).T
  fc_bench.bench(Lfun,setLagrange00,LN=LN)
  
def bench_Lagrange():
  import fc_bench
  import numpy as np
  Lfun=[Lagrange,lagint]
  names=['Lag','lagint']
  error=lambda o1,o2: np.linalg.norm(o1-o2,np.inf)
  n=[5,9,15]; m=[100,500,1000];
  N,M=np.meshgrid(n,m)
  LN=np.vstack((N.flatten(),M.flatten())).T
  fc_bench.bench(Lfun,setLagrange,LN=LN,error=error, names=names, info=False,labelsinfo=True, a=-1,b=1,fun='lambda x: np.sin(x)')  
  
def bench_MatProd00():
  import fc_bench
  import numpy as np
  Lfun=[np.matmul]
  LN=np.arange(500,4001,500)
  fc_bench.bench(Lfun,setMatProd00,LN=LN)  
  
def bench_MatProd01():
  import fc_bench
  import numpy as np
  Lfun=[np.matmul]
  comment=['# Benchmarking function numpy.matmul', 
           '# where X and Y are (m,m) Numpy arrays']
  LN=np.arange(500,4001,500)
  fc_bench.bench(Lfun,setMatProd01,LN=LN, comment=comment, savefile='MadProd01.out')    
  
def bench_MatProd02():
  import fc_bench
  import numpy as np
  Lfun=[np.matmul]
  comment=['# Benchmarking function numpy.matmul', 
           '# where X and Y are (m,m) Numpy arrays']
  LN=np.arange(500,4001,500)
  fc_bench.bench(Lfun,setMatProd02,LN=LN, comment=comment, savefile='MadProd02')    

  
def matprod01(A,B):
  import numpy as np
  (n,m)=A.shape
  (p,q)=B.shape
  assert m==p,'shapes %s and %s not aligned: %d (dim 1) != %d (dim 0)'%(str(A.shape),str(B.shape),A.shape[1],B.shape[0])
  C=np.zeros((n,q))
  for i in np.arange(n):
    for j in np.arange(q):
      for k in np.arange(m):
        C[i,j]+=A[i,k]*B[k,j]
  return C

def matprod02(A,B):
  import numpy as np
  (n,m)=A.shape
  (p,q)=B.shape
  #if np.iscomplexobj(A) or np.iscomplexobj(B):
    #dot=np.vdot
  #else:
    #dot=np.dot
  assert m==p,'shapes %s and %s not aligned: %d (dim 1) != %d (dim 0)'%(str(A.shape),str(B.shape),A.shape[1],B.shape[0])
  if np.iscomplexobj(A) or np.iscomplexobj(B):
    C=1j*np.zeros((n,q))
  else:
    C=np.zeros((n,q))
  for i in np.arange(n):
    for j in np.arange(q):
      C[i,j]=np.dot(A[i],B[:,j])
  return C

#try:
if sys.version_info > (3, 5):
  from fc_bench.demos_op  import *
else:
  def bench_MatProd03():
    import fc_bench
    import numpy as np
    Lfun=[np.matmul,matprod01]
    comment=['# Benchmarking function numpy.matmul', 
            '# where X and Y are (m,m) Numpy arrays']
    LN=np.arange(50,201,50)
    fc_bench.bench(Lfun,setMatProd02,LN=LN, comment=comment)
  
  def bench_MatProd04():
    import sys,fc_bench
    import numpy as np
    Lfun=[np.matmul,matprod01]
    names=['matmul(X,Y)','']
    comment=['# Benchmarking function numpy.matmul', 
            '# where X and Y are (m,m) Numpy arrays']
    LN=np.arange(50,201,50)
    fc_bench.bench(Lfun,setMatProd02,LN=LN, comment=comment, names=names)  
  
  def bench_MatProd05():
    import sys,fc_bench
    import numpy as np
    Lfun=[np.matmul,matprod02]
    error=lambda o1,o2: np.linalg.norm(o1-o2,np.inf)
    names=['matmul(X,Y)','']
    comment=['# Benchmarking functions:',
            '#     A1=numpy.matmul(X,Y) (reference)',
            '#     A2= fc_bench.demos.matprod02(X,Y)',
            '# where X and Y are (m,m) Numpy arrays',
            '# cmpErr[1] is the norm(A1-A2,Inf)']
    LN=np.arange(100,401,100)
    fc_bench.bench(Lfun,setMatProd02,LN=LN, comment=comment, names=names, info=False, error=error)
    
  def bench_MatProd05bis():
    import fc_bench
    import numpy as np
    Lfun=[np.matmul,fc_bench.demos.matprod02]
    error=lambda o1,o2: np.linalg.norm(o1-o2,np.inf)
    names=['matmul(X,Y)','']
    LN=np.arange(100,401,100)
    fc_bench.bench(Lfun,fc_bench.demos.setMatProd02,LN=LN, names=names, info=False,labelsinfo=True, error=error)    
 
  def bench_MatProd06():
    import sys,fc_bench
    import numpy as np
    Lfun=[np.matmul,matprod02]
    error=lambda o1,o2: np.linalg.norm(o1-o2,np.inf)
    names=['matmul(X,Y)','']
    comment=['# Benchmarking functions:',
            '#     A1=numpy.matmul(X,Y) (reference)',
            '#     A2= fc_bench.demos.matprod02(X,Y)',
            '# where X and Y are respectively (m,n) and (n,p) Numpy arrays',
            '# cmpErr[1] is the norm(A1-A2,Inf)']
    LN=[ [100,50,100],[150,50,100],[200,50,100],[150,100,300]]
    fc_bench.bench(Lfun,setMatProd03,LN=LN, lcomplex=True, rtype=np.dtype('f4'),
                  comment=comment, names=names, info=False, error=error) 
    
def permLU(A):
  (m,n)=A.shape
  assert m==n
  U=A.copy()
  p=np.arange(n)
  L=np.eye(m)
  for k in np.arange(m-1):
    mu=np.argmax(abs(U[k:,k]))+k
    if abs(U[mu,k])> 1e-15:
      if mu!=k:
        U[[k,mu],k:]=U[[mu,k],k:]
        L[[k,mu],:k]=L[[mu,k],:k]
        p[[k,mu]]=p[[mu,k]]
      for j in np.arange(k+1,m):
        L[j,k]=U[j,k]/U[k,k]
        U[j,k:]+=-L[j,k]*U[k,k:]
  return L,U,permInd2Mat(p)
  
def permInd2Mat(p):
  n=len(p)
  I=np.arange(n,dtype=np.int)
  P=np.zeros((n,n))
  P[I,p]=1
  return P

def setLU00(m,verbose,**kwargs):
  Print=kwargs.get('Print',lambda s: print(s))
  from fc_bench.bench import bData
  A=np.random.randn(m,m)
  if verbose:
    Print('# input parameter: (m,m) Numpy array')
    
  bDs=[bData('{:>8}'.format('m'),m,'{:>8}')]
  return ((A),bDs)

def bench_LU00():
  import fc_bench
  import numpy as np
  Lfun=[permLU]
  comment=['# Benchmarking function fc_bench.demos.permLU function (LU factorization)']
  LN=np.arange(100,401,100)
  fc_bench.bench(Lfun,setLU00,LN=LN, comment=comment)
  
def setLU01(m,verbose,**kwargs):
  import fc_tools
  Print=kwargs.get('Print',lambda s: print(s))
  from fc_bench.bench import bData
  A=np.random.randn(m,m)
  Error=lambda L,U,P: np.linalg.norm(np.matmul(L,U)-np.matmul(P,A),np.inf);
  if verbose:
    Print('# input parameter: (m,m) Numpy array')
    Print('# Outputs are [L,U,P] such that P*A=L*U')
    Print('# Error[i] computed with fun[i] outputs :\n#   %s'%fc_tools.others.func2str(Error,source=False))
  bDs=[bData('{:>8}'.format('m'),m,'{:>8}')]
  return ((A,Error),bDs)  

def bench_LU01():
  import fc_bench
  import numpy as np
  Lfun=[permLU]
  comment=['# Benchmarking function fc_bench.demos.permLU function (LU factorization)']
  LN=np.arange(100,401,100)
  fc_bench.bench(Lfun,setLU01,LN=LN, comment=comment)
  
def scipyLU(A):
  from scipy.linalg import lu
  P,L,U=lu(A)
  return L,U,P.T

def bench_LU02():
  import fc_bench
  import numpy as np
  Lfun=[scipyLU,permLU]
  comment=['# Benchmarking functions(LU factorization):',
           '#   fun[1]:  fc_bench.demos.scipyLU',
           '#   fun[1]:  fc_bench.demos.permLU']
  cmpErr=lambda o1,o2: np.linalg.norm(o1[0]-o2[0],np.inf)+\
                       np.linalg.norm(o1[1]-o2[1],np.inf)+\
                       np.linalg.norm(o1[2]-o2[2],np.inf)
  LN=np.arange(100,401,100)
  fc_bench.bench(Lfun,setLU01,LN=LN, comment=comment,error=cmpErr)

def alldemos(short=True):
  import fc_tools
  from fc_bench.bench import strfun
  if short:
    Ldem=[bench_Lagrange,bench_MatProd02,bench_MatProd05,bench_MatProd06,bench_LU02]
  else:
    Ldem=[bench_Lagrange00,bench_Lagrange,
          bench_MatProd00,bench_MatProd01,bench_MatProd02,bench_MatProd03,
          bench_MatProd04,bench_MatProd05,bench_MatProd05bis,bench_MatProd06,
          bench_LU00,bench_LU01,bench_LU02]
  i=1
  soft,release=fc_tools.Sys.getSoftware()
  for demo in Ldem:
    print('\n\n*********** Running demo [%2d/%2d]: %s'%(i,len(Ldem), strfun(demo))) 
    print('*********** With %s %s\n'%(soft,release))
    demo()
    i+=1
    
  
