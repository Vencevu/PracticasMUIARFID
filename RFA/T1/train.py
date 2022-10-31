import math
import sys
import numpy as np
from sklearn import metrics
from sklearn.linear_model import LogisticRegression

if len(sys.argv)!=3:
  print('Usage: %s <trdata> <devdata>' % sys.argv[0])
  sys.exit(1)

tr=np.load(sys.argv[1])['tr']; 
dv=np.load(sys.argv[2])['dv']; 
N,L=tr.shape
D=L-1
Xtr=tr[:,1:D]
xltr=tr[:,-1]
Xdv=dv[:,1:D]
xldv=dv[:,-1]

clf = LogisticRegression().fit(Xtr, xltr)

probs = clf.predict_proba(Xdv)[:,1]
auc = metrics.roc_auc_score(xldv,probs)
print("Dev AUC: %.1f%%" % (auc*100))

estimated_xldv = clf.predict(Xdv)
err = (xldv != estimated_xldv).sum()/Xdv.shape[0]; 
r=1.96*math.sqrt(err*(1-err)/Xdv.shape[0])
print("Dev CER: %.2f%% [%.2f, %.2f]" % (err*100,(err-r)*100,(err+r)*100))
