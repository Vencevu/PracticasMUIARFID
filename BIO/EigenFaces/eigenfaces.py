import sys
import os
import matplotlib.pyplot as plt
import numpy as np
from numpy import linalg as LA
from sklearn.neighbors import KNeighborsClassifier

v = int(sys.argv[1])

def cargar_pgm(archivo):
    with open(archivo) as f:
        lines = f.readlines()

    lines = [l for l in lines if not l.startswith('#')]
    assert lines[0].strip() == 'P2'

    data = []
    for line in lines[1:]:
        data.extend([int(c) for c in line.split()])

    return np.array(data[3:]), (data[1], data[0]), data[2]

def cargar_datos():
    x_train = []
    y_train = []
    x_test = []
    y_test = []
    Nc = []
    for ruta, _, archivos in os.walk("../data/IDENTIFICACION/ORLProcessed/Train/", topdown=False):
        Nc.append(len(archivos))
        for archivo in archivos:
            etiqueta = int(ruta[-3:].split('s')[1])
            y_train.append(etiqueta)

            imagen = cargar_pgm(os.path.join(ruta, archivo))
            x_train.append(imagen[0])
    for ruta, _, archivos in os.walk("../data/IDENTIFICACION/ORLProcessed/Test/", topdown=False):
        for archivo in archivos:
            etiqueta = int(ruta[-3:].split('s')[1])
            y_test.append(etiqueta)

            imagen = cargar_pgm(os.path.join(ruta, archivo))
            x_test.append(imagen[0])
    x_train = np.asarray(x_train, dtype=np.float64).T
    y_train = np.asarray(y_train)
    x_test = np.asarray(x_test, dtype=np.float64).T
    y_test = np.asarray(y_test)

    Nc.pop(0)
    return x_train, y_train, x_test, y_test, Nc

def PCA(x_train, x_test, d_):
    d, n = x_train.shape

    mu = np.mean(x_train, axis=1, keepdims=True)

    A = x_train - mu

    C_ = np.dot(A.T, A) / d

    delta_, B_ = LA.eig(C_)

    B = np.dot(A, B_)
    delta = (d / n) * delta_

    ordenados = np.flip(np.argsort(delta))
    delta = delta[ordenados]
    B = B[:, ordenados]

    normas = LA.norm(B, axis=0)
    B = B / normas

    Bd = B[:, :d_]
    Bdt = Bd.T
    x_train_red = np.dot(Bdt, (x_train - mu))
    x_test_red = np.dot(Bdt, (x_test - mu))

    return x_train_red, x_test_red

def knn(v, x_train, y_train, x_test, y_test):
    vecino = KNeighborsClassifier(n_neighbors=v, metric='euclidean', p=2)
    vecino.fit(x_train.T, y_train)
    y_pred = vecino.predict(x_test.T)
    precision = np.sum(y_pred == y_test) / len(y_pred)
    return precision

if __name__ == "__main__":
    x_train, y_train, x_test, y_test, Nc = cargar_datos()
    precisiones = []
    reducciones = np.arange(5, 205, 5)
    for d_ in reducciones:
        x_train_red, x_test_red = PCA(x_train, x_test, d_)
        precision = knn(v, x_train_red, y_train, x_test_red, y_test)
        precisiones.append(precision)

    max_precision = max(precisiones)
    indice = precisiones.index(max_precision)
    mejor_reduccion = reducciones[indice]
    print(f"La mejor reducción es {mejor_reduccion}, con una precisión de {max_precision}")
    title = f"Reducción PCA y Clasificación con {v}-NN"
    plt.title(title)
    plt.plot(reducciones, precisiones)
    plt.xlabel("Valor de d'")
    plt.ylabel("Precisión (%)")
    nombre = f"Resultados_PCA_{v}nn.png"
    plt.savefig(nombre)