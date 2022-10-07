from collections import Counter
import random
from numpy.random import randint
import math
import csv

def simulated_annealing(initial_state, jugadores):
    """Peforms simulated annealing to find a solution"""
    initial_temp = 900
    final_temp = .1
    alpha = 0.01
    
    current_temp = initial_temp
    
    # Start by initializing the current state with the initial state
    current_state = initial_state
    solution = current_state

    while current_temp > final_temp:
        neighbor = random.choice(get_neighbors(current_state, jugadores))

        # Check if neighbor is best so far
        cost_diff = get_cost(current_state, jugadores) - get_cost(neighbor, jugadores)

        # if the new solution is better, accept it
        if cost_diff < 0:
            current_state = neighbor
            solution = current_state
            print("New Best: ", solution)
        # if the new solution is not better, accept it with a probability of e^(-cost/temp)
        else:
            if random.uniform(0, 1) < math.exp(-cost_diff / current_temp):
                solution = neighbor
                print("Worst accepted: ", solution)
        # decrement the temperature
        current_temp -= alpha

    return solution

def get_cost(state, jugadores):
    """Calculates cost of the argument state for your solution."""
    puntos, coste = 0, 0
    posiciones = []
    for gen in state:
        puntos += jugadores[gen]["puntos"]
        coste += jugadores[gen]["precio"]
        posiciones.append(jugadores[gen]["tipo"])
    puntos /= len(state)
    contador = Counter(posiciones)
    if coste <= 60000 and contador[0] == contador[1] == contador[2] == contador[3] and contador[4] == 1:
        return puntos
    else:
        return -puntos
    
def get_neighbors(state, jugadores):
    """Returns neighbors of the argument state for your solution."""
    res = []
    for _ in range(10):
        new_state = [x for x in state]
        new_state[randint(0, 9)] = randint(0, len(jugadores)-1)
        res.append(new_state)
    return res

def cargarJugadores():
	res = {}
	with open("jugadores.csv") as f:
		reader = csv.reader(f, delimiter=';')
		for row in reader:
			res[int(row[0])] = {"nombre": row[1], "tipo": int(row[2]), "puntos": float(row[3]), "precio": int(row[4])}
	return res

jugadores = cargarJugadores()
init_state = [random.randint(0, len(jugadores)-1) for _ in range(9)]
best = simulated_annealing(init_state, jugadores)
print("Done", best)
for j in best:
    print(jugadores[j])
print('Coste: %i' % (sum([jugadores[j]["precio"] for j in best])))
print('Puntuacion: %i' % (sum([jugadores[j]["puntos"] for j in best])/len(best)))