import sys
import numpy as np
import pickle
from sklearn import metrics
import math

if len(sys.argv)!=3:
  print('Usage: %s <model> <devdata>' % sys.argv[0])
  sys.exit(1)

dv=np.load(sys.argv[2])['dv']
clf = pickle.load(open(sys.argv[1], 'rb'))
N,L=dv.shape
D=L-1

Xdv=dv[:,1:D]
xldv=dv[:,-1]

probs = clf.predict_proba(Xdv)[:,1]
auc = metrics.roc_auc_score(xldv,probs)
print("AUC: %.1f%%" % (auc*100))

estimated_xldv = clf.predict(Xdv)
err = (xldv != estimated_xldv).sum()/Xdv.shape[0]; 
r=1.96*math.sqrt(err*(1-err)/Xdv.shape[0])
print("CER: %.2f%% [%.2f, %.2f]" % (err*100,(err-r)*100,(err+r)*100))