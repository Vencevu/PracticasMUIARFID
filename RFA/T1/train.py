import math
import sys
import numpy as np
from scipy.special import softmax
from sklearn import metrics, preprocessing
from sklearn.linear_model import LogisticRegression

if len(sys.argv)!=3:
  print('Usage: %s <trdata> <devdata>' % sys.argv[0])
  sys.exit(1)

tr=np.load(sys.argv[1])['dv']
dv=np.load(sys.argv[2])['tr']

N,L=tr.shape
D=L-1

Xtr=tr[:,1:D]
xltr=tr[:,-1]
Xdv=dv[:,1:D]
xldv=dv[:,-1]

probFB = np.average(Xtr[:, 9:12], axis=1)
Xtr = np.c_[np.c_[Xtr[:, 0:9], probFB], Xtr[:, 12:]]

probFB = np.average(Xdv[:, 9:12], axis=1)
Xdv = np.c_[np.c_[Xdv[:, 0:9], probFB], Xdv[:, 12:]]

clf = LogisticRegression().fit(Xtr, xltr)

probs = clf.predict_proba(Xdv)[:,1]
auc = metrics.roc_auc_score(xldv,probs)
print("Dev AUC: %.1f%%" % (auc*100))

estimated_xldv = clf.predict(Xdv)
err = (xldv != estimated_xldv).sum()/Xdv.shape[0]; 
r=1.96*math.sqrt(err*(1-err)/Xdv.shape[0])
print("Dev CER: %.2f%% [%.2f, %.2f]" % (err*100,(err-r)*100,(err+r)*100))
