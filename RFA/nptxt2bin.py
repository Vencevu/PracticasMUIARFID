import sys
import numpy as np

if len(sys.argv)!=3:
  print('Usage: %s <trdata> <dvdata>' % sys.argv[0]);
  sys.exit(1);

tr=np.loadtxt(sys.argv[1]);
dv=np.loadtxt(sys.argv[2]);

np.savez_compressed(sys.argv[1]+'.npz', tr=tr)
np.savez_compressed(sys.argv[2]+'.npz', dv=dv)
