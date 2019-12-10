factorial(1,1).
factorial(N,S):-N > 1, N1 is N-1, factorial(N1,S1), S is N*S1.