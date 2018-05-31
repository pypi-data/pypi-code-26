import sys

assert sys.version_info > (3, 5),'Incompatible Python version with @ operator'
  
def bench_MatProd03():
  import fc_bench
  import numpy as np
  Lfun=[np.matmul,lambda X,Y: X@Y,fc_bench.demos.matprod01]
  comment=['# Benchmarking function numpy.matmul', 
          '# where X and Y are m-by-m Numpy arrays']
  LN=np.arange(50,201,50)
  fc_bench.bench(Lfun,fc_bench.demos.setMatProd02,LN=LN, comment=comment)
  
def bench_MatProd04():
  import fc_bench
  import numpy as np
  Lfun=[np.matmul,lambda X,Y: X@Y,fc_bench.demos.matprod01]
  names=['matmul(X,Y)','X@Y','']
  comment=['# Benchmarking function numpy.matmul', 
           '# where X and Y are m-by-m Numpy arrays']
  LN=np.arange(50,201,50)
  fc_bench.bench(Lfun,fc_bench.demos.setMatProd02,LN=LN, comment=comment, names=names)
  
def bench_MatProd05():
  import fc_bench
  import numpy as np
  Lfun=[np.matmul,lambda X,Y: X@Y ,fc_bench.demos.matprod02]
  error=lambda o1,o2: np.linalg.norm(o1-o2,np.inf)
  names=['matmul(X,Y)','X@Y','']
  comment=['# Benchmarking functions:',
           '#     A1=numpy.matmul(X,Y) (reference)',
           '#     A2= X@Y',
           '#     A3= fc_bench.demos.matprod02(X,Y)',
           '# where X and Y are m-by-m Numpy arrays',
           '# cmpErr[1] is the norm(A1-A2,Inf)',
           '# cmpErr[2] is the norm(A1-A3,Inf)']
  LN=np.arange(100,401,100)
  fc_bench.bench(Lfun,fc_bench.demos.setMatProd02,LN=LN, comment=comment, names=names, info=False, error=error)  
  
def bench_MatProd05bis():
  import fc_bench
  import numpy as np
  # with labelsinfo, <lambda> function must be alone on a code line 
  # (otherwise not well  guessed)
  f=lambda X,Y: X@Y
  Lfun=[np.matmul,f,fc_bench.demos.matprod02]
  error=lambda o1,o2: np.linalg.norm(o1-o2,np.inf)
  names=['matmul(X,Y)','X@Y','']
  LN=np.arange(100,401,100)
  fc_bench.bench(Lfun,fc_bench.demos.setMatProd02,LN=LN, names=names, info=False,labelsinfo=True, error=error)    
  
def bench_MatProd06():
  import fc_bench
  import numpy as np
  Lfun=[np.matmul,lambda X,Y: X@Y,fc_bench.demos.matprod02]
  error=lambda o1,o2: np.linalg.norm(o1-o2,np.inf)
  names=['matmul(X,Y)','X@Y','']
  comment=['# Benchmarking functions:',
           '#     A1=numpy.matmul(X,Y) (reference)',
           '#     A2= X@Y',
           '#     A3= fc_bench.demos.matprod02(X,Y)',
           '# where X and Y are respectively (m,n) and (n,p) Numpy arrays',
           '# cmpErr[1] is the norm(A1-A2,Inf)',
           '# cmpErr[2] is the norm(A1-A3,Inf)']
  LN=[ [100,50,100],[150,50,100],[200,50,100],[150,100,300]]
  fc_bench.bench(Lfun,fc_bench.demos.setMatProd03,LN=LN, lcomplex=True, rtype=np.dtype('f4'),
                 comment=comment, names=names, info=False, error=error)   
