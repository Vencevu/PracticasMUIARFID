import sys
import numpy as np
from sklearn.linear_model import LogisticRegression
import pickle

if len(sys.argv)!=3:
  print('Usage: %s <trdata> <devdata>' % sys.argv[0]);
  sys.exit(1);

tr=np.load(sys.argv[1])['tr']; 
dv=np.load(sys.argv[2])['dv'];
N,L=tr.shape; D=L-1;

Xtr=tr[:,1:D]; xltr=tr[:,-1];
Xdv=dv[:,1:D]; xldv=dv[:,-1];
Xtr=np.concatenate((Xtr,Xdv));
xltr=np.concatenate((xltr,xldv));

clf = LogisticRegression().fit(Xtr, xltr)

filename = 'model.sav'
pickle.dump(clf, open(filename, 'wb'))
