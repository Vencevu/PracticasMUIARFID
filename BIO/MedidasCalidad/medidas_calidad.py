import sys
import matplotlib.pyplot as plt
import numpy as np

"""
INSTRUCCIONES DE USO
Ejecutamos en la terminal la instrucción python3 medidas_calidad.py c i x1 x2 ... xn
-> 'c' e 'i' son los archivos de scores de clientes e impostores del sistema determinado (A o B)
-> 'x1', 'x2' ... 'xn' son los distintos valores de x para los que se desea calcular 
    FP(FN=x), el umbral FN=x, FN(FP=x) y el umbral FP=x
"""

#Procesamos los datos obtenidos de los clientes e impostores

##Los resultados (scores de cada persona) se guardan en 'scores_cli' y 'scores_impost'
##Guardamos en la lista 'scores' los resultados junto con una etiqeuta de clase (0->Cliente, 1->Impostor)
##La lista 'scores' está ordenada de mejor a peor resultado

cli = sys.argv[1]
impost = sys.argv[2]

with open(cli) as f:
    clientes = list(f)
with open(impost) as f:
    impostores = list(f)

scores_cli = []
scores_impost = []
for cliente in clientes:
    scores_cli.append(float(cliente.split(" ")[1]))
for impostor in impostores:
    scores_impost.append(float(impostor.split(" ")[1]))

scores = []
for score in scores_cli:
    scores.append((score, 0))
for score in scores_impost:
    scores.append((score, 1))

scores = sorted(scores, key=lambda t: t[0])

#Cálculo de la curva ROC

##Guardamos, para cada posible valor de thr, el porcentaje de FP en rocX y el de 1-FN en rocY

rocX = []
rocY = []
for score in scores:
    thr, fn, fp = score[0], 0, 0
    for s in scores:
        if s[1]==0 and s[0]<=thr:
            fn += 1
        if s[1]==1 and s[0]>thr:
            fp += 1
    fp = fp/len(scores_impost)
    fn = fn/len(scores_cli)

    rocX.append(fp)
    rocY.append(1-fn)

#Cálculo de FP(FN=X), umbral FN=X, FN(FP=X) y umbral FP=X

##El método mindistance devuelve, dada una lista l y un número n, la posición 
##del elemento de l que se encuentra a menor distancia de n

def mindistance(n, l):
    distancia = 2
    elegido = None
    for i in l:
        if distancia > abs(i-n):
            distancia = abs(i-n)
            elegido = i
    return l.index(elegido)

def FP_FN_umbral(x):
    posicion = mindistance(x, listaFN)
    valor = rocX[posicion]
    umbral = scores[posicion][0]
    return valor, umbral

def FN_FP_umbral(x):
    posicion = mindistance(x, rocX)
    valor = listaFN[posicion]
    umbral = scores[posicion][0]
    return valor, umbral

valores_x = []

for i in range(3, len(sys.argv)):
    valores_x.append(float(sys.argv[i]))

##Dado que en nuestra lista tenemos 1-FN, hay que obtener otra con FN
listaFN = []
for i in rocY:
    listaFN.append(1-i)

for x in valores_x:
    valorFPFN, umbralFPFN = FP_FN_umbral(x)
    valorFNFP, umbralFNFP = FN_FP_umbral(x)
    print("Para x=%f:" % x)
    print("     El umbral FN=x es %f y FP(FN=x) es %f" % (umbralFPFN, valorFPFN)) 
    print("     El umbral FP=x es %f y FN(FP=x) es %f" % (umbralFNFP, valorFNFP))

#Cálculo del umbral FP=FN

listaDistancias = []
for i in range(len(rocX)):
    listaDistancias.append(abs(rocX[i]-listaFN[i]))

arg_min = np.argmin(listaDistancias)

umbral_FNFP = scores[arg_min][0]

print("El umbral FN=FP es %f" % umbral_FNFP)

#Cálculo del área bajo la curva ROC

areaROC = 0
for i in scores_cli:
    for j in scores_impost:
        if i>j:
            areaROC += 1
areaROC = areaROC/(len(scores_cli)*len(scores_impost))

#Dibujamos, para cada valor de x, la curva ROC y su área y la guardamos en una imagen .png

fig = plt.figure()
plt.plot(rocX, rocY)
plt.fill_between(rocX, rocY, facecolor='blue', alpha=0.25)
plt.text(0.25, 0.5, areaROC, fontsize=12)
plt.xlabel("FP")
plt.ylabel("1-FN")
fig.savefig("curvaRoc.png")
plt.show()

print("La curva ROC se ha generado en una imagen .png y el área bajo esta es de %f" % areaROC)

#Cálculo del factor d-prime

media_pos = sum(scores_cli)/len(scores_cli)
media_neg = sum(scores_impost)/len(scores_impost)

desv_tip_pos = 0
sumatorio = 0
for i in range(len(scores_cli)):
    x = scores_cli[i]
    sumatorio += (x-media_pos)**2
desv_tip_pos = np.sqrt(sumatorio/len(scores_cli))

desv_tip_neg = 0
sumatorio = 0
for i in range(len(scores_impost)):
    x = scores_impost[i]
    sumatorio += (x-media_neg)**2
desv_tip_neg = np.sqrt(sumatorio/len(scores_impost))

dprime = (media_pos-media_neg)/(np.sqrt((desv_tip_pos**2)+(desv_tip_neg**2)))

print("El factor dprime obtenido es %f" % dprime)