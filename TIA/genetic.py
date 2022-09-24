from numpy.random import randint
from numpy.random import rand
import argparse
import names
import random

# Funcion Objetivo
def fo(individuo, jugadores):
	puntos = sum([jugadores[t]["puntos"] for t in individuo])/len(individuo)
	coste = sum([jugadores[t]["precio"] for t in individuo])
	if coste <= 60000:
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
	c1 = p1.copy()
	if rand() < r_cross:
		pt = randint(1, len(p1)-2)
		c1 = p1[:pt] + p2[pt:]
	return [c1]

# Mutacion
def mutation(individuo, r_mut, jugadores):
	for i in range(len(individuo)):
		if rand() < r_mut:
			individuo[i] = randint(0, len(jugadores)-1)

# Algoritmo Genetico mamalongo
def genetic_algorithm(objective, n_iter, n_pop, r_cross, r_mut, jugadores):
	# Poblacion Inicial
	pop = [randint(0, len(jugadores) - 1, 9).tolist() for _ in range(n_pop)]
	best, best_eval = 0, objective(pop[0], jugadores)
	# Generaciones
	for gen in range(n_iter):
		# Evaluamos a todos los individuos
		scores = [objective(c, jugadores) for c in pop]
		# Buscamos al mejor individuo
		for i in range(n_pop):
			if scores[i] > best_eval:
				best, best_eval = pop[i], scores[i]
				print(">%d, new best f(%s) = %.3f" % (gen,  pop[i], scores[i]))
		# Padres seleccionados
		selected = [selection(pop, scores) for _ in range(n_pop)]
		# Siguiente generacion
		children = list()
		for i in range(0, n_pop, 2):
			# Cogemos los padres por pares
			p1, p2 = selected[i], selected[i+1]
			# Cruce y mutacion
			for c in crossover(p1, p2, r_cross):
				mutation(c, r_mut, jugadores)
				children.append(c)
		# Reemplazamos poblacion
		pop = pop[int(len(pop)/2):]+children
	return [best, best_eval]

def generarJugadores(n, generarNombres):
	res = {}
	for i in range(0, n):
		p = round(random.uniform(10.0, 80.0),2)
		res[i] = {"tipo": randint(0, 4), "puntos": p, "precio": randint(int(2000*p/10), int(3000*p/10))}
		if(generarNombres):
			res[i]["nombre"] = names.get_full_name()
	return res


parser = argparse.ArgumentParser(description='Algoritmo genetico para seleccionar jugadores de baloncesto')

parser.add_argument('generaciones', type=int,
                    help='Numero de generaciones')

parser.add_argument('poblacion', type=int,
                    help='Tamaño de la poblacion')

parser.add_argument('r_mut', type=float,
                    help='Ratio de mutacion')

parser.add_argument('r_cruce', type=float,
                    help='Ratio de cruce')

parser.add_argument('--nombres', action='store_true',
                    help='Generar nombres para los jugadores')

args = parser.parse_args()

generaciones = args.generaciones
tamaño_poblacion = args.poblacion
jugadores = generarJugadores(1000, args.nombres)
r_cross = args.r_cruce
r_mut = args.r_mut

best, score = genetic_algorithm(fo, generaciones, tamaño_poblacion, r_cross, r_mut, jugadores)
print('Done!')
for j in best:
	print(jugadores[j])
print('Coste: %i' % (sum([jugadores[j]["precio"] for j in best])))
print('Puntuacion: %i' % (sum([jugadores[j]["puntos"] for j in best])/len(best)))