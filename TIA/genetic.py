from operator import countOf
from numpy.random import randint
from numpy.random import rand
import matplotlib.pyplot as plt
import argparse
import csv
import random

# Funcion Objetivo
def fo(individuo, jugadores):
	puntos = sum([jugadores[t]["puntos"] for t in individuo])/len(individuo)
	coste = sum([jugadores[t]["precio"] for t in individuo])
	num0 = countOf([jugadores[t]["tipo"] for t in individuo], 0) == 2
	num1 = countOf([jugadores[t]["tipo"] for t in individuo], 1) == 2
	num2 = countOf([jugadores[t]["tipo"] for t in individuo], 2) == 2
	num3 = countOf([jugadores[t]["tipo"] for t in individuo], 3) == 2
	num4 = countOf([jugadores[t]["tipo"] for t in individuo], 4) == 1
	if coste <= 60000 and num0 and num1 and num2 and num3 and num4:
		return puntos
	else:
		return 0

# Seleccion por competicion
def selection(pop, scores, k=3):
	# Seleccionamos un individuo aleatorio
	selection_ix = randint(len(pop))
	for ix in randint(0, len(pop), k-1):
		# buscamos un individuo mejor
		if scores[ix] > scores[selection_ix]:
			selection_ix = ix
	return pop[selection_ix]

# Cruce de dos padres para crear dos hijos
def crossover(p1, p2, r_cross):
	# Los hijos son copias de los padres por defecto
	c1, c2 = p1.copy(), p2.copy()
	if rand() < r_cross:
		pt = randint(1, len(p1)-2)
		c1 = p1[:pt] + p2[pt:]
		c2 = p1[pt:] + p2[:pt]
	return [c1, c2]

# Reemplazo de la poblacion
def pop_replace(pop, children, inmortales):
	new_pop = []
	no_elements_to_keep = len(pop) // 2
	new_pop = random.sample(pop, no_elements_to_keep) + children
	for inmortal in inmortales:
		if inmortal not in new_pop:
			new_pop.append(inmortal)
	return new_pop


# Mutacion
def mutation(individuo, r_mut, jugadores):
	for i in range(len(individuo)):
		if rand() < r_mut:
			individuo[i] = randint(0, len(jugadores)-1)

# Algoritmo Genetico mamalongo
def genetic_algorithm(objective, n_iter, n_pop, r_cross, r_mut, jugadores):
	inmortales = list()
	llamadas_fitness = 0
	registro = [(0, 0)]
	# Poblacion Inicial
	pop = [randint(0, len(jugadores) - 1, 9).tolist() for _ in range(n_pop)]
	best, best_eval = pop[0], objective(pop[0], jugadores)
	
	# Generaciones
	for gen in range(n_iter):
		# Evaluamos a todos los individuos
		scores = [objective(c, jugadores) for c in pop]
		llamadas_fitness += len(pop)
		# Buscamos al mejor individuo
		for i in range(len(pop)):
			if scores[i] > best_eval:
				best, best_eval = pop[i], scores[i]
				print(">%d, new best f(%s) = %.3f" % (gen,  pop[i], scores[i]))
				registro.append((best_eval, llamadas_fitness))
		# Los mejores no mueren
		if best not in inmortales and best != 0:
			inmortales.append(best)
		# Padres seleccionados
		selected = [selection(pop, scores) for _ in range(len(pop)//2)]
		# Siguiente generacion
		children = list()
		for i in range(0, len(selected), 2):
			# Cogemos los padres por pares
			if i+1 >= len(selected):
				p1, p2 = selected[i], selected[randint(0, len(selected))]
			else:
				p1, p2 = selected[i], selected[i+1]
			# Cruce y mutacion
			for c in crossover(p1, p2, r_cross):
				mutation(c, r_mut, jugadores)
				children.append(c)
		# Reemplazamos poblacion
		pop = pop_replace(pop, children, inmortales)
		if gen == n_iter - 1:
			registro.append((best_eval, gen))
	return [best, best_eval, registro]

def cargarJugadores():
	res = {}
	with open("jugadores.csv") as f:
		reader = csv.reader(f, delimiter=';')
		for row in reader:
			res[int(row[0])] = {"nombre": row[1], "tipo": int(row[2]), "puntos": float(row[3]), "precio": int(row[4])}
	return res

parser = argparse.ArgumentParser(description='Algoritmo genetico para seleccionar jugadores de baloncesto')

parser.add_argument('-g', type=int,
                    help='Numero de generaciones')

parser.add_argument("-p", type=int, default=[], nargs="+",
					help="Tamaños de poblacion iniciales")

parser.add_argument('-rm', type=float,
                    help='Ratio de mutacion')

parser.add_argument('-rc', type=float,
                    help='Ratio de cruce')

args = parser.parse_args()

generaciones = args.g
tamaño_poblacion = args.p
jugadores = cargarJugadores()
r_cross = args.rc
r_mut = args.rm

for poblacion in tamaño_poblacion:
	best, score, resultados = genetic_algorithm(fo, generaciones, poblacion, r_cross, r_mut, jugadores)
	print(resultados)
	print('Done!')
	for j in best:
		print(jugadores[j])
	print('Coste: %i' % (sum([jugadores[j]["precio"] for j in best])))
	print('Puntuacion: %i' % (sum([jugadores[j]["puntos"] for j in best])/len(best)))

	x = [i[1] for i in resultados]
	y = [i[0] for i in resultados]

	plt.plot(x, y, label=str(poblacion))

plt.title("Mutacion %.2f Cruce %.2f" % (r_mut, r_cross))
plt.xlabel("Soluciones generadas")
plt.legend(loc="upper left")
plt.ylabel("Fitness")
plt.show()