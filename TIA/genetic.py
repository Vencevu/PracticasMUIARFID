from numpy.random import randint
from numpy.random import rand

# Funcion Objetivo
def fo(x, y):
	return sum([y[t]["puntos"] for t in x])

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
	# check for recombination
	if rand() < r_cross:
		# select crossover point that is not on the end of the string
		pt = randint(1, len(p1)-2)
		# Hacemos el cruce
		c1 = p1[:pt] + p2[pt:]
		c2 = p2[:pt] + p1[pt:]
	return [c1, c2]

# Mutacion
def mutation(bitstring, r_mut, jugadores):
	for i in range(len(bitstring)):
		# check for a mutation
		if rand() < r_mut:
			# flip the bit
			bitstring[i] = randint(0, len(jugadores)-1)

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
		pop = children
	return [best, best_eval]

iteraciones = 100
tamaño_poblacion = 100
jugadores = {
    0:{"tipo":0, "puntos":16.5, "precio":500},
    1:{"tipo":1, "puntos":26.5, "precio":700},
    2:{"tipo":2, "puntos":46.5, "precio":400},
    3:{"tipo":3, "puntos":6.5, "precio":200},
    4:{"tipo":0, "puntos":76.5, "precio":1000},
    5:{"tipo":1, "puntos":36.5, "precio":600},
    6:{"tipo":2, "puntos":56.5, "precio":800},
    7:{"tipo":3, "puntos":66.5, "precio":700},
    8:{"tipo":0, "puntos":26.5, "precio":200},
    9:{"tipo":1, "puntos":86.5, "precio":900},
    10:{"tipo":2, "puntos":26.5, "precio":300},
    11:{"tipo":3, "puntos":36.5, "precio":600},
    12:{"tipo":0, "puntos":46.5, "precio":400},
    13:{"tipo":1, "puntos":26.5, "precio":300},
    }
# crossover rate
r_cross = 0.9
# mutation rate
r_mut = 1.0 / float(7)
# perform the genetic algorithm search
best, score = genetic_algorithm(fo, iteraciones, tamaño_poblacion, r_cross, r_mut, jugadores)
print('Done!')
print('f(%s) = %f' % (best, score))