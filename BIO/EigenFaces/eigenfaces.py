import sys
import os 
import matplotlib as plt
import numpy as np  
from numpy import linalg as LA              
import matplotlib.pyplot as plt   
from sklearn.neighbors import KNeighborsClassifier

##Parámetro k del algoritmo de k-vecinos más cercanos.
v = int(sys.argv[1])

##Método obtenido de StackOverflow para procesar imágenes y almacenarlas en 
##un vector de numpy.
def read_pgm(name):
    with open(name) as f:
        lines = f.readlines()

    # Ignores commented lines
    for l in list(lines):
        if l[0] == '#':
            lines.remove(l)

    # Makes sure it is ASCII format (P2)
    assert lines[0].strip() == 'P2' 

    # Converts data to a list of integers
    data = []
    for line in lines[1:]:
        data.extend([int(c) for c in line.split()])

    return (np.array(data[3:]),(data[1],data[0]),data[2])

##Definimos un método para cargar los datos.
##Es necesario que la carpeta OCR esté en la misma ruta que el presente script.
##Cada imagen se almacena en un array de numpy.
##Todos estos se guardan en un array multidimensional y se convierte en una matriz de numpy.
def procesarDatos():
    x_training = []
    y_training = []
    x_test = []
    y_test = []
    Nc = []
    for ruta, directorios, archivos in os.walk("../data/IDENTIFICACION/ORLProcessed/Train/", topdown=False):
        Nc.append(len(archivos))
        for archivo in archivos:
            etiqueta = int(ruta[-3:].split('s')[1])
            y_training.append(etiqueta)
            
            imagen = read_pgm(os.path.join(ruta, archivo))
            x_training.append(imagen[0])
    for ruta, directorios, archivos in os.walk("../data/IDENTIFICACION/ORLProcessed/Test/", topdown=False):
        for archivo in archivos:
            etiqueta = int(ruta[-3:].split('s')[1])
            y_test.append(etiqueta)
            
            imagen = read_pgm(os.path.join(ruta, archivo))
            x_test.append(imagen[0])
    x_training = np.asarray(x_training, dtype=np.float64).T
    y_training = np.asarray(y_training)
    x_test = np.asarray(x_test, dtype=np.float64).T
    y_test = np.asarray(y_test)
    
    Nc.pop(0)
    return x_training, y_training, x_test, y_test, Nc

##Definimos un método para PCA donde le pasamos los datos (entrenamiento y test) y la reducción
##que le queremos aplicar, devolviéndonos los datos con la dimensionalidad reducida.
def PCA(x_training, x_test, d_):
    #Obtenemos las d features de las n imágenes de training
    d = x_training.shape[0]
    n = x_training.shape[1]
    
    #Calculamos el vector promedio (cara promedio)
    mu = np.mean(x_training, axis=1, keepdims=True)

    #Calculamos la matriz A donde almacenamos la diferencia de cada vector con el promedio 
    A = np.zeros((d, n), dtype=np.float64)
    A = np.asarray(A)
    for i in range(n):
        A[:,i] = x_training[:, i] - mu[:,0]

    #Calculamos los eigevalues y los eigenvectores de la matriz de covarianzas de las muestras.
    #Para ello seguimos las consideraciones prácticas de las transparencias, en las que
    #primero se calcula un C_ de nxn junto con sus eigenvalues y eigenvectores.
    # C_ = np.asarray(A.T) * np.asarray(A)
    C_ = np.dot(A.T, A)
    C_ /= d

    delta_, B_ = LA.eig(C_)

    # B = np.asarray(A) * np.asarray(B_)
    B = np.dot(A, B_)
    delta = (d/n) * delta_

    #Ordenamos los eigenvectores y eigenvalues; y normalizamos estos últimos
    ordenados = np.flip(np.argsort(delta))
    delta = delta[ordenados]
    B = B[:,ordenados] 

    normas = LA.norm(B, axis=0)
    B = B / normas

    #Aplicamos la reducción con los d_ primeros eigenvectores
    Bd = B[:,:d_]
    Bdt = Bd.T
    x_training_red = np.dot(Bdt, (x_training - mu))
    x_test_red = np.dot(Bdt, (x_test - mu))

    return x_training_red, x_test_red

##Definimos un método para el k-vecino más cercano donde le pasamos el
##parámetro k que indica el número de vecinos más cercanos; y los datos 
##de entrenamiento y test, junto con las etiquetas.
##El método es un algoritmo de entrenamiento/clasificación que devuelve la precisión 
##obtenida con los datos de entrada.
def kvecino(v, x_training, y_training, x_test, y_test):
    vecino = KNeighborsClassifier(n_neighbors = v, metric ='euclidean', p = 2)
    #Entrenamos con k-nn
    vecino.fit(x_training.T, y_training)
    #Clasificamos con k-nn
    y_pred = vecino.predict(x_test.T)
    #Calculamos la precisión de nuestro clasificador
    precision = 0
    for i in range(len(y_pred)):
        if y_pred[i]==y_test[i]:
            precision += 1
    precision = precision/len(y_pred)
    return precision

##Implementamos EigenFaces.
if __name__ == "__main__":
    x_training, y_training, x_test, y_test, Nc = procesarDatos()
    precisiones = []
    reducciones = [i for i in np.arange(5, 205, 5)]
    for d_ in reducciones:
        x_training_red, x_test_red = PCA(x_training, x_test, d_)
        precision = kvecino(v, x_training_red, y_training, x_test_red, y_test)
        precisiones.append(precision)

    max_precision = max(precisiones)
    indice = precisiones.index(max_precision)
    mejor_reduccion = reducciones[indice]
    print("La mejor reducción es %d, con una precision de %f" % (mejor_reduccion, max_precision))
    title = "Reducción PCA y Clasificación con "+str(v)+"-NN"
    plt.title(title)
    plt.plot(reducciones, precisiones)
    plt.xlabel("Valor de d'")
    plt.ylabel("Precisión (%)")
    nombre = "Resultados_PCA_"+str(v)+"nn.png"
    plt.savefig(nombre)