import sys
import numpy as np
from sklearn import metrics
from sklearn.linear_model import LogisticRegression
import pickle
import matplotlib.pyplot as plt

if len(sys.argv)!=3:
  print('Usage: %s <devdata> <model>' % sys.argv[0]);
  sys.exit(1);

dv=np.load(sys.argv[1])['dv'];
N,L=dv.shape; D=L-1;
Xdv=dv[:,1:D]; xldv=dv[:,-1];

clf = pickle.load(open(sys.argv[2], 'rb'))

probs = clf.predict_proba(Xdv)[:,1];

fpr, tpr, _ = metrics.roc_curve(xldv,probs,pos_label=1);  

plt.plot(fpr,tpr)
plt.ylabel('True Positive Rate')
plt.xlabel('False Positive Rate')
plt.show()
