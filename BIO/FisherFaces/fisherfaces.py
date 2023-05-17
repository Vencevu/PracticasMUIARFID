import sys
import os 
import matplotlib as plt
import numpy as np  
from numpy import linalg as LA              
import matplotlib.pyplot as plt   
from sklearn.neighbors import KNeighborsClassifier

def read_pgm(archivo):
    with open(archivo) as f:
        lines = f.readlines()

    for l in list(lines):
        if l[0] == '#':
            lines.remove(l)

    assert lines[0].strip() == 'P2' 

    data = []
    for line in lines[1:]:
        data.extend([int(c) for c in line.split()])

    return (np.array(data[3:]),(data[1],data[0]),data[2])

def procesarDatos():
    x_train = []
    y_train = []
    x_test = []
    y_test = []
    Nc = []
    for ruta, _ , archivos in os.walk("../data/IDENTIFICACION/ORLProcessed/Train/", topdown=False):
        Nc.append(len(archivos))
        for archivo in archivos:
            etiqueta = int(ruta[-3:].split('s')[1])
            y_train.append(etiqueta)
            
            imagen = read_pgm(os.path.join(ruta, archivo))
            x_train.append(imagen[0])
    for ruta, _ , archivos in os.walk("../data/IDENTIFICACION/ORLProcessed/Test/", topdown=False):
        for archivo in archivos:
            etiqueta = int(ruta[-3:].split('s')[1])
            y_test.append(etiqueta)
            
            imagen = read_pgm(os.path.join(ruta, archivo))
            x_test.append(imagen[0])
    x_train = np.asarray(x_train, dtype=np.float64).T
    y_train = np.asarray(y_train)
    x_test = np.asarray(x_test, dtype=np.float64).T
    y_test = np.asarray(y_test)
    
    return x_train, y_train, x_test, y_test, Nc

def PCA(x_train, x_test, d_):
    d = x_train.shape[0]
    n = x_train.shape[1]
    
    mu = np.mean(x_train, axis=1, keepdims=True)

    A = np.zeros((d, n), dtype=np.float64)
    A = np.asarray(A)
    for i in range(n):
        A[:,i] = x_train[:, i] - mu[:,0]

    C_ = np.dot(A.T, A)
    C_ /= d

    delta_, B_ = LA.eig(C_)

    B = np.dot(A, B_)
    delta = (d/n) * delta_

    ordenados = np.flip(np.argsort(delta))
    delta = delta[ordenados]
    B = B[:,ordenados] 

    normas = LA.norm(B, axis=0)
    B = B / normas

    Bd = B[:,:d_]
    Bdt = Bd.T
    x_train_red = np.dot(Bdt, (x_train - mu))
    x_test_red = np.dot(Bdt, (x_test - mu))

    return x_train_red, x_test_red

def kvecino(v, x_train, y_train, x_test, y_test):
    vecino = KNeighborsClassifier(n_neighbors = v, metric ='euclidean', p = 2)
    vecino.fit(x_train.T, y_train)
    y_pred = vecino.predict(x_test.T)
    precision = 0
    for i in range(len(y_pred)):
        if y_pred[i]==y_test[i]:
            precision += 1
    precision = precision/len(y_pred)
    return precision

v = int(sys.argv[1])
d_pca = int(sys.argv[2])

def LDA(x_training, x_test, Nc, d_):
    mu = np.mean(x_training, axis=1)
    
    mu_c = []
    for i, nc in enumerate(Nc):
        j=nc
        while j>0:
            mu_c.append(x_training[:,i*nc:(i*nc)+nc].mean(axis=1))
            j-=1
    mu_c = np.asarray(np.array(mu_c)).T
    if mu_c.shape[1]==1:
        mu_c = mu_c.T

    Sb = np.mat(mu_c) - np.mat(mu).T
    
    nc = np.mean(Nc)
    Sb = nc * Sb * Sb.T
    
    Sw = x_training - mu_c
    Sw = np.mat(Sw) * np.mat(Sw).T
    C = LA.inv(Sw)*Sb

    delta, B = LA.eigh(C)

    ordenados = np.flip(np.argsort(delta))
    delta = delta[ordenados]
    B = B[:,ordenados] 

    Bd = B[:,:d_]
    Bdt = Bd.T
    x_training_red = Bdt * x_training
    x_test_red = Bdt * x_test

    return x_training_red, x_test_red

x_training, y_training, x_test, y_test, Nc = procesarDatos()
precisiones = []
reduccionesLDA = [i for i in np.arange(5, 205, 5)]
for d_lda in reduccionesLDA:
    x_training_pca, x_test_pca = PCA(x_training, x_test, d_pca)
    x_training_lda, x_test_lda = LDA(x_training_pca, x_test_pca, Nc, d_lda)
    precision = kvecino(v, x_training_lda, y_training, x_test_lda, y_test)
    precisiones.append(precision)

max_precision = max(precisiones)
indice = precisiones.index(max_precision)
mejor_reduccion = reduccionesLDA[indice]
print("Con una reducción previa de PCA de %d, la mejor reducción con LDA es %d, obteniendo una precision de %f" % (d_pca, mejor_reduccion, max_precision))
title = "Reducción PCA+LDA y Clasificación con "+str(v)+"-NN"
plt.title(title)
plt.plot(reduccionesLDA, precisiones)
plt.xlabel("Valor de d' para LDA con una reducción previa de %d con PCA" % d_pca)
plt.ylabel("Precisión (%)")
nombre = "Resultados_PCA_LDA_"+str(v)+"nn.png"
plt.savefig(nombre)