from numpy.random import randint
from numpy.random import rand
import random

# Funcion Objetivo
def fo(x, y):
	return sum([y[t]["puntos"] for t in x])/len(x)

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

def generarJugadores(n):
	res = {}
	for i in range(0, n):
		res[i] = {"tipo": randint(0, 4), "puntos": round(random.uniform(10.0, 80.0),2), "precio": randint(200, 10000)}
	return res

generaciones = 100
tamaño_poblacion = 100
jugadores = generarJugadores(1000)
# Ratio de cruce
r_cross = 0.9
# Ratio de mutacion
r_mut = 1.0 / float(7)

best, score = genetic_algorithm(fo, generaciones, tamaño_poblacion, r_cross, r_mut, jugadores)
print('Done!')
print('f(%s) = %f' % (best, score))