#!/home/users/sage00/sage0020/venv2/bin/pyclovis
import dosna
import numpy as np
ds='test3'
dosna.use('cpu', 'sage')
a=dosna.Connection('test', conffile='pyclovis_test.conf')
a.connect()
b=np.arange(1,28).reshape((3,3,3))
c=a.create_dataset(ds, data=b)
print(c[:])
c.delete()
a.disconnect()