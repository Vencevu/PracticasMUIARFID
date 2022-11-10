import math
import sys
import numpy as np
from scipy.special import softmax
from sklearn import metrics, preprocessing
from sklearn.linear_model import LogisticRegression

#Softmax + escalado
def softmaxScale(Xtr, Xdv):
	XtrS = softmax(Xtr, axis=1)
	XdvS = softmax(Xdv, axis=1)
	scaler = preprocessing.StandardScaler().fit(XtrS)
	Xtr_scaled = scaler.transform(Xtr)
	scaler = preprocessing.StandardScaler().fit(XdvS)
	Xdv_scaled = scaler.transform(Xdv)

	return Xtr_scaled, Xdv_scaled

#Reduce las dimensiones de las características haciendo la media desde la componente i hasta la j
def avgProp(i,j, Xtr, Xdv):
	probFB = np.average(Xtr[:, i:j], axis=1)
	resTr = np.c_[np.c_[Xtr[:, 0:i], probFB], Xtr[:, j:]]
	probFB = np.average(Xdv[:, i:j], axis=1)
	resDv = np.c_[np.c_[Xdv[:, 0:i], probFB], Xdv[:, j:]]

	return resTr, resDv

if len(sys.argv)!=3:
  print('Usage: %s <trdata> <devdata>' % sys.argv[0])
  sys.exit(1)

#para polimedia las keys dv y tr estan invertidas
tr=np.load(sys.argv[1])['dv']
dv=np.load(sys.argv[2])['tr']
N,L=tr.shape
D=L-1

Xtr=tr[:,1:D]
xltr=tr[:,-1]
Xdv=dv[:,1:D]
xldv=dv[:,-1]
print("Procesando datos...")
Xtr, Xdv = avgProp(0, 3, Xtr, Xdv)
print("Entrenando...")
clf = LogisticRegression().fit(Xtr, xltr)
print("Validando...")
probs = clf.predict_proba(Xdv)[:,1]
auc = metrics.roc_auc_score(xldv,probs)
print("Dev AUC: %.1f%%" % (auc*100))

estimated_xldv = clf.predict(Xdv)
err = (xldv != estimated_xldv).sum()/Xdv.shape[0]; 
r=1.96*math.sqrt(err*(1-err)/Xdv.shape[0])
print("Dev CER: %.2f%% [%.2f, %.2f]" % (err*100,(err-r)*100,(err+r)*100))
