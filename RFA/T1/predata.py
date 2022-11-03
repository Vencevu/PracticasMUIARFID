import math
import sys
import numpy as np

if len(sys.argv)!=2:
  print('Usage: %s <trdata>' % sys.argv[0])
  sys.exit(1)

tr=np.load(sys.argv[1])['tr']
N,L=tr.shape
D=L-1
Xtr=tr[:,1:D]
xltr=tr[:,-1]

print(Xtr)