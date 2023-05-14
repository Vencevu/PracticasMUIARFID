import sys
import matplotlib.pyplot as plt
import numpy as np

"""
INSTRUCCIONES DE USO
python medidas_calidad.py c i x1 x2 ... xn
-> 'c' e 'i' son los archivos de scores de clientes e impostores
-> 'x1', 'x2' ... 'xn' son las x para calcular 
    FP(FN=x), el umbral FN=x, FN(FP=x) y el umbral FP=x
"""

cli = sys.argv[1]
impost = sys.argv[2]

with open(cli) as f:
    clientes = list(f)

with open(impost) as f:
    impostores = list(f)

scores_clientes = []
scores_impostores = []
for cliente in clientes:
    scores_clientes.append(float(cliente.split(" ")[1]))
for impostor in impostores:
    scores_impostores.append(float(impostor.split(" ")[1]))

scores = []
for score in scores_clientes:
    scores.append((score, 0))
for score in scores_impostores:
    scores.append((score, 1))

scores = sorted(scores, key=lambda t: t[0])

rocX = []
rocY = []
for score in scores:
    thr, fn, fp = score[0], 0, 0
    for s in scores:
        if s[1]==0 and s[0]<=thr:
            fn += 1
        if s[1]==1 and s[0]>thr:
            fp += 1
    fp = fp/len(scores_impostores)
    fn = fn/len(scores_clientes)

    rocX.append(fp)
    rocY.append(1-fn)


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

listaFN = []
for i in rocY:
    listaFN.append(1-i)

for x in valores_x:
    valorFPFN, umbralFPFN = FP_FN_umbral(x)
    valorFNFP, umbralFNFP = FN_FP_umbral(x)
    print("Para x=%f:" % x)
    print("     Umbral FN=x es %f y FP(FN=x) es %f" % (umbralFPFN, valorFPFN)) 
    print("     Umbral FP=x es %f y FN(FP=x) es %f" % (umbralFNFP, valorFNFP))

listaDistancias = []
for i in range(len(rocX)):
    listaDistancias.append(abs(rocX[i]-listaFN[i]))

arg_min = np.argmin(listaDistancias)

umbral_FNFP = scores[arg_min][0]

print("El umbral FN=FP es %f" % umbral_FNFP)

areaROC = 0
for i in scores_clientes:
    for j in scores_impostores:
        if i>j:
            areaROC += 1
areaROC = areaROC/(len(scores_clientes)*len(scores_impostores))

fig = plt.figure()
plt.plot(rocX, rocY)
plt.xlabel("FP")
plt.ylabel("1-FN")
plt.text(0.25, 0.5, areaROC, fontsize=11)
plt.fill_between(rocX, rocY, facecolor='blue', alpha=0.25)
fig.savefig("curvaRoc.png")
plt.show()

print("La curva ROC se ha generado en una imagen .png y el área bajo esta es de %f" % areaROC)

media_pos = sum(scores_clientes)/len(scores_clientes)
media_neg = sum(scores_impostores)/len(scores_impostores)

desv_tip_pos = 0
sumatorio = 0
for i in range(len(scores_clientes)):
    x = scores_clientes[i]
    sumatorio += (x-media_pos)**2
desv_tip_pos = np.sqrt(sumatorio/len(scores_clientes))

desv_tip_neg = 0
sumatorio = 0
for i in range(len(scores_impostores)):
    x = scores_impostores[i]
    sumatorio += (x-media_neg)**2
desv_tip_neg = np.sqrt(sumatorio/len(scores_impostores))

dprime = (media_pos-media_neg)/(np.sqrt((desv_tip_pos**2)+(desv_tip_neg**2)))

print("El factor dprime obtenido es %f" % dprime)