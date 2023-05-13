import numpy as np
from random import shuffle
import pandas as pd
import requests
from scipy.stats import pearsonr
import tmdbsimple as tmdb
from os.path import exists
import os

class Recomendador():
    """
    Clase que representa un sistema de recomendacion
    Attributes
    ----------
    preferencias : numpy.matrix
        matriz de preferencias con los 6 géneros favoritos de cada usuario
    pref_hyb : numpy.matrix
        matriz de preferencias con los 6 géneros favoritos de cada usuario según su grupo demográfico
    pref_dg : numpy.matrix
        matriz de preferencias con los 6 géneros favoritos de cada grupo demográfico
    grupos_demograficos : dict
        diccionario donde la clave es el usuario y el valor el grupo demográfico al que pertenece
    user : int
        id del usuario que ha iniciado sesión. Si nadie ha iniciado sesión su valor es -1
    users_df : pandas.DataFrame
        DataFrame con los usuarios registrados
    ratings : pandas.DataFrame
        DataFrame con las puntuaciones de cada pelicula por cada usuario
    generos : pandas.DataFrame
        DataFrame con los géneros de las películas registradas
    films_df : pandas.DataFrame
        DataFrame con las películas registradas
    Methods
    -------
    register_user(age, gender : str, occupation : str) -> None
        Da de alta a un usuario
    log_in(self, user, passwd) -> bool
        Inicia sesión en la cuenta de un usuario registrado. Devuelve True si el inicio ha sido correcto, False en otro caso.
    
    load_grupos_demograficos() -> None
        Carga el diccionario de grupos demográficos
    
    rate_film(film, score) -> None
        Puntua una película por un usuario agregando el registro a films_df
    
    obtener_recomendacion(user : int, n: int) -> list
        Devuelve una lista de n películas recomendadas para el id de usuario user
    
    get_user_films(user : int) -> list
        Devuelve una lista con las películas que el usuario con id user ha puntuado
    save_user_pref(user : int, user_pref : list) -> None
        Guarda las preferencias del usuario user
    """
    def __init__(self, data_path) -> None:
        """
        Parameters
        ----------
        data_path : str
            Directorio donde se almacenan los archivos de datos del sistema (genre.txt, items.txt, u1_base.txt y users.txt)
        """
        tmdb.REQUESTS_SESSION = requests.Session()
        tmdb.API_KEY = '1e11e7d4c5f3aad6e459fc0f63bfb0f5'
        tmdb.REQUESTS_TIMEOUT = 5

        self.preferencias_coop = []
        self.pref_hyb = []
        self.pref_dg = []
        self.grupos_demograficos = {}
        self.data_path = data_path

        #Usuario que inicia sesion
        self.user = -1
        
        self.users_df = pd.read_csv(data_path+"/users.txt", names=["user_id", "age", "gender", "occupation", "user_name"], sep="\t",dtype={
                    'user_id': 'int64',
                    'age': 'int64',
                    'gender': 'object',
                    'occupation': 'object',
                    'user_name': 'object',
                 })
        self.ratings = pd.read_csv(data_path+"/u1_base.txt", names=["user_id", "movie_id", "rating"], sep="\t")
        self.generos = pd.read_csv(data_path+"/genre.txt", names=["genre_id", "genre_name"], sep="\t")
        all_genre = self.generos.genre_name.values.tolist()
        all_genre = ["movie_id"] + all_genre + ["title"]
        self.films_df = pd.read_csv(data_path+"/items.txt",encoding="iso-8859-1" ,names=all_genre, sep="\t")
        if exists(data_path+"/films.txt"):
            film_id_df = pd.read_csv(data_path+"/films.txt",encoding="iso-8859-1", sep="\t",names=["movie_id","tmdb_id"])
            film_id_df['movie_id']=film_id_df['movie_id'].astype(int)
            self.films_df = self.films_df.merge(film_id_df,on="movie_id")
        else:
            film_id_df = self.preprocess_films()
            self.films_df = self.films_df.merge(film_id_df,on="movie_id")
        # print(self.films_df)

    def save_data(self, path='.'):
        self.users_df.to_csv(path+'/users.txt', header=None, index=None, sep='\t', mode='w')
        self.ratings.to_csv(path+'/u1_base.txt', header=None, index=None, sep='\t', mode='w')
        self.films_df.to_csv(path+'/items.txt', header=None, index=None, sep='\t', mode='w')
    
    def register_user(self, age, gender, occupation, nickname) -> None:
        """Regsitra a un nuevo usuario
        Parameters
        ----------
        age : int
            Edad
        gender : str
            Sexo
        occupation : str
            Profesion
        Returns
        -------
        None
        """
        self.users_df.loc[len(self.users_df.index)] = [len(self.users_df.index)+1, age, gender, occupation, nickname]
        self.save_data()
    
    def log_in(self, user, passwd) -> bool:
        """Inicia sesión
        Parameters
        ----------
        user : int
            Id del usuario
        passwd : str
            Contraseña
        Returns
        -------
        bool
            Devuelve True si se ha iniciado sesión correctamente, False en otro caso
        """
        user = self.users_df[self.users_df['user_name'] == user]['user_name'].tolist()
        if len(user) > 0 and passwd == "inicio"+str(user[0]):
            self.user = user[0]
            return True
        
        return False
    
    def log_out(self) -> None:
        self.user = -1
    
    def get_username_id(self,username) -> None:
        return self.users_df[self.users_df['user_name'] == username]['user_id'].tolist()[0]
    
    def get_user_films(self, user : int) -> list:
        """Obtiene las películas puntuadas por un usuario y sus notas
        Parameters
        ----------
        user : int
            Id del usuario
        Returns
        -------
        list
            una lista con los ids de las películas, otra lista con las notas
        """
        res = []
        res = self.ratings[self.ratings.user_id == user]['movie_id'].tolist()
        notas = []
        for i in res:
            notas.append(self.get_user_film_rate(user,i))
        return [res,notas]

    def rate_film(self, film, score) -> None:
        """Puntúa una película por el usuario que ha inciado sesión
        Parameters
        ----------
        film : int
            Id de la película
        score : float
            Puntuación
        Returns
        -------
        None
        """
        if self.ratings[(self.ratings.movie_id == film) & (self.ratings.user_id == self.user)].size == 0:
            self.ratings.loc[len(self.ratings.index)] = [self.user, film, score]
        else:
            self.ratings.loc[self.ratings[(self.ratings.movie_id == film) & (self.ratings.user_id == self.user)].index[0]] = [self.user,film,score]

    def get_hyb_pref(self):
        pref_hyb = []
        for u in self.ratings.user_id.unique().tolist():
            if (type(self.preferencias_coop) in [np.ndarray, list]) & (type(self.pref_dg) in [np.ndarray, list]):
                pref = (np.sum(np.matrix([self.preferencias_coop[u-1], self.pref_dg[self.grupos_demograficos[u]-1]]), axis=0)/2).tolist()[0]
            if (type(self.preferencias_coop) == np.matrix) & (type(self.pref_dg) in [np.ndarray, list]):
                pref = (np.sum(np.matrix([self.preferencias_coop[u-1].tolist()[0], self.pref_dg[self.grupos_demograficos[u]-1]]), axis=0)/2).tolist()[0]
            if (type(self.preferencias_coop) in [np.ndarray, list]) & (type(self.pref_dg) == np.matrix):
                pref = (np.sum(np.matrix([self.preferencias_coop[u-1], self.pref_dg[self.grupos_demograficos[u]-1].tolist()[0]]), axis=0)/2).tolist()[0]
            if (type(self.preferencias_coop) == np.matrix) & (type(self.pref_dg) in [np.ndarray, list]):
                pref = (np.sum(np.matrix([self.preferencias_coop[u-1].tolist()[0], self.pref_dg[self.grupos_demograficos[u]-1].tolist()[0]]), axis=0)/2).tolist()[0]
            pref_hyb.append(pref)

        return np.matrix(pref_hyb)

    def load_grupos_demograficos(self) -> None:
        """Rellena el atributo grupos_demograficos
        
        Returns
        -------
        None
        """

        def get_user_type(gender, age, occupation):
            res = 0
            group1 = ['doctor', 'healthcare', 'entertainment']
            group2 = ['engineer', 'programmer', 'scientist', 'technician']
            group3 = ['artist', 'writer', 'librarian', 'homemaker']
            group4 = ['none', 'other', 'student', 'retired']
            group5 = ['executive', 'lawyer', 'administrator', 'salesman', 'marketing']

            if occupation in group1:
                if age < 23:
                    res = 1 if gender == 'M' else 2
                elif 24 < age < 40:
                    res = 3 if gender == 'M' else 4
                elif 41 < age < 60:
                    res = 5 if gender == 'M' else 6
                else:
                    res = 7 if gender == 'M' else 8
            elif occupation in group2:
                if age < 23:
                    res = 9 if gender == 'M' else 9
                elif 24 < age < 40:
                    res = 11 if gender == 'M' else 12
                elif 41 < age < 60:
                    res = 13 if gender == 'M' else 14
                else:
                    res = 15 if gender == 'M' else 16
            elif occupation in group3:
                if age < 23:
                    res = 17 if gender == 'M' else 18
                elif 24 < age < 40:
                    res = 19 if gender == 'M' else 20
                elif 41 < age < 60:
                    res = 21 if gender == 'M' else 22
                else:
                    res = 23 if gender == 'M' else 24
            elif occupation in group4:
                if age < 23:
                    res = 25 if gender == 'M' else 26
                elif 24 < age < 40:
                    res = 27 if gender == 'M' else 28
                elif 41 < age < 60:
                    res = 29 if gender == 'M' else 30
                else:
                    res = 31 if gender == 'M' else 32
            elif occupation in group5:
                if age < 23:
                    res = 33 if gender == 'M' else 34
                elif 24 < age < 40:
                    res = 35 if gender == 'M' else 36
                elif 41 < age < 60:
                    res = 37 if gender == 'M' else 38
                else:
                    res = 39 if gender == 'M' else 40

            return res - 1 if res > 9 else res

        self.grupos_demograficos = {}
        for user_id in self.users_df.user_id.unique().tolist():
            user = self.users_df[self.users_df.user_id == user_id]
            user_demo_group = get_user_type(user.gender.tolist()[0], user.age.tolist()[0], user.occupation.tolist()[0])
            self.grupos_demograficos[user_id] = user_demo_group

    def get_pref(self):
        res = []
        for u in self.ratings.user_id.unique().tolist():
            best_genres = []
            for i in self.generos['genre_name'].tolist():
                puntos = self.genre_seen(u, i)
                if puntos > 2.5:
                    best_genres.append((i, puntos))

            best_genres.sort(key=lambda a: a[1], reverse=True)
            best_genres = best_genres[:6]
            pref = []
            
            for genero in self.generos['genre_name'].tolist():
                add = False
                for bg in best_genres:
                    if genero == bg[0]:
                        add = True
                        break
                if add:
                    pref.append(bg[1])
                else:
                    pref.append(0)

            res.append(pref)

        return res
    
    def load_preferencias(self, path="", path_dg="", path_hyb="") -> None:
        """Carga las matrices de preferencias
        Parameters
        ----------
        path : str
            Ruta del archivo de preferencias
        path_dg : str
            Ruta del archivo de preferencias demográficas
        path_dg : str
            Ruta del archivo de preferencias híbridas
        Returns
        -------
        None
        """
        self.preferencias_coop = np.load(path)['a'] if path != "" else self.get_pref()
        self.pref_dg = np.load(path_dg)['a'] if path_dg != "" else self.get_dg_pref()
        self.pref_hyb = np.load(path_hyb)['a'] if path_hyb != "" else self.get_hyb_pref()

        self.save_preferencias()
        self.preferencias_coop = np.load('../data/preferencias.npz')['a']
        self.pref_dg = np.load('../data/preferencias_demografico.npz')['a']
        self.pref_hyb = np.load('../data/preferencias_hibrido.npz')['a']
        
    def save_preferencias(self, path="../data") -> None:
        """Guarda las matrices de preferencias en sus respectivos archivos
        Parameters
        ----------
        path : str
            Ruta del directorio en el que se guardan los archivos
        Returns
        -------
        None
        """
        np.savez_compressed(path+"/preferencias", a=self.preferencias_coop)
        np.savez_compressed(path+"/preferencias_demografico", a=self.pref_dg)
        np.savez_compressed(path+"/preferencias_hibrido", a=self.pref_hyb)

    def movie_votes_demographic(self, grupos, movie_id, grupo):
        usuarios = [k for k, v in grupos.items() if v == grupo]
        return len(self.ratings[(self.ratings.user_id.isin(usuarios)) & (self.ratings.movie_id == movie_id)].index), self.ratings[(self.ratings.user_id.isin(usuarios)) & (self.ratings.movie_id == movie_id)].mean()['rating'], self.ratings[self.ratings.movie_id == movie_id].mean()['rating']

    def save_user_pref(self,user, user_pref) -> None:
        if user > self.preferencias_coop.shape[0]:
            self.preferencias_coop = np.append(self.preferencias_coop, [user_pref], axis=0)
        else:
            self.preferencias_coop[user-1,:] = user_pref

    def genre_seen(self, user_id, genre_name):
        scores = []
        for film_id in self.ratings[self.ratings['user_id'] == user_id].movie_id.tolist():
            if self.films_df[self.films_df['movie_id'] == film_id][genre_name].tolist()[0] == 1:
                scores.append(self.ratings[(self.ratings['movie_id'] == film_id) & (self.ratings['user_id'] == user_id)]['rating'].tolist()[0])

        return sum(scores)/len(scores) if scores != [] else 0

    def get_genres_score(self, users):

        def take(n, iterable):
            res = {}
            i = 0
            for k, v in iterable.items():
                if i >= n:
                    break
                res[k] = v
                i += 1
                
            return res
    
        best_genres = {}
        for u in users:
            for i in self.generos['genre_name'].tolist():
                puntos = self.genre_seen(u, i)
                if puntos > 2.5:
                    if i not in best_genres.keys():
                        best_genres[i] = puntos/len(users)
                    else:
                        best_genres[i] += puntos/len(users)

        best_genres = {k: v for k, v in sorted(best_genres.items(), key=lambda item: item[1])}
        best_genres = take(6, best_genres)

        pref = []

        for genero in self.generos['genre_name'].tolist():
            add = False
            for k, v in best_genres.items():
                if genero == k:
                    add = True
                    break
            if add:
                pref.append(v)
            else:
                pref.append(0)

        return pref

    def obtener_vecinos(self, preferencias, user, k=1) -> tuple:
        vecinos = [0]*k
        vecinos_score = [0]*k
        pref = preferencias[user]
        for i in range(0, preferencias.shape[0]):
            if i == user:
                continue
            score = pearsonr(pref, preferencias[i])[0]
            if score > min(vecinos_score):
                vecinos[vecinos_score.index(min(vecinos_score))] = i + 1
                vecinos_score[vecinos_score.index(min(vecinos_score))] = score
                
        res = (vecinos, vecinos_score)
        vecinos2, vecinos_score2 = [], []
        for _ in res[0]:
            max_val = vecinos.index(max(vecinos_score))
        return vecinos, vecinos_score

    def obtener_recomendacion_cooperativa(self, user, n) -> list:
        """Obtiene películas recomendadas para un usuario
        Parameters
        ----------
        user : int
            Id del usuario
        Returns
        -------
        list
            Lista con los ids de las películas
        """
        vecino = self.obtener_vecinos(self.preferencias_coop, 0, 1)
        pelis_user = self.ratings[self.ratings.user_id == user]['movie_id'].tolist()
        pelis_vecino = self.ratings[self.ratings.user_id == vecino[0][0]][['movie_id', 'rating']].sort_values(by=['rating'], ascending=False)['movie_id'].tolist()
        return [x for x in pelis_vecino if x not in pelis_user][:n]
    
    def obtener_recomendacion_contenido(self, user, n) -> list:
        """Obtiene películas recomendadas para un usuario por contenido
        Parameters
        ----------
        user : int
            Id del usuario
        Returns
        -------
        list
            Lista con los ids de las películas
        """
        res = []
        aux = 0
        pelis_user = self.ratings[(self.ratings.user_id == user) & (self.ratings.rating > 3)].sort_values(by='rating', ascending=False)['movie_id'].tolist()
        if len(pelis_user) == 0:
            res = self.films_df.iloc[:, [i + 1 for i in self.generos.loc[np.argpartition(self.preferencias_coop[user], -4)[-6:]]['genre_id'].tolist()]].sum(axis=1).sort_values(ascending=False).keys()
            return res[:n]
        for p in pelis_user:
            x = self.films_df[self.films_df.movie_id == p]
            r = self.films_df[(self.films_df['Action'] == x['Action'].tolist()[0]) &
                              (self.films_df['Adventure'] == x['Adventure'].tolist()[0]) &
                              (self.films_df['Adventure'] == x['Animation'].tolist()[0]) &
                              (self.films_df["Children's"] == x["Children's"].tolist()[0]) &
                              (self.films_df['Comedy'] == x['Comedy'].tolist()[0]) &
                              (self.films_df['Crime'] == x['Crime'].tolist()[0]) &
                              (self.films_df['Documentary'] == x['Documentary'].tolist()[0]) &
                              (self.films_df['Drama'] == x['Drama'].tolist()[0]) &
                              (self.films_df['Fantasy'] == x['Fantasy'].tolist()[0]) &
                              (self.films_df['Film-Noir'] == x['Film-Noir'].tolist()[0]) &
                              (self.films_df['Horror'] == x['Horror'].tolist()[0]) &
                              (self.films_df['Musical'] == x['Musical'].tolist()[0]) &
                              (self.films_df['Mystery'] == x['Mystery'].tolist()[0]) &
                              (self.films_df['Romance'] == x['Romance'].tolist()[0]) &
                              (self.films_df['Sci-Fi'] == x['Sci-Fi'].tolist()[0]) &
                              (self.films_df['Thriller'] == x['Thriller'].tolist()[0]) &
                              (self.films_df['War'] == x['War'].tolist()[0]) &
                              (self.films_df['Western'] == x['Western'].tolist()[0])
                              ]['movie_id'].tolist()

            if len(r) > 0:
                if r[0] not in res:
                    res.append(r[0])
                    aux+=1

            if aux >= n:
                break
            
        return list(set(res))

    def obtener_recomendacion_dg(self, user, n) -> list:
        """Obtiene películas recomendadas por grupo demográfico para un usuario
        Parameters
        ----------
        user : int
            Id del usuario
        Returns
        -------
        list
            Lista con los ids de las películas
        """
        if self.grupos_demograficos == []:
            print("Falta cargar los grupos demográficos, load_grupos_demograficos()")
            return []

        grupo = self.grupos_demograficos[user]
        vecino = self.obtener_vecinos(self.pref_dg, grupo, 1)
        pelis_user = self.ratings[self.ratings.user_id == user]['movie_id'].tolist()
        pelis_vecino = self.ratings[self.ratings.user_id == vecino[0][0]][['movie_id', 'rating']].sort_values(by=['rating'], ascending=False)['movie_id'].tolist()
        return [x for x in pelis_vecino if x not in pelis_user][:n]
    
    def obtener_recomendacion_hyb(self, user, recomendadores, n) -> list:
        """Obtiene películas recomendadas de modo híbrido para un usuario
        Parameters
        ----------
        user : int
            Id del usuario
        recomendadores : list
            lista de recomendadores a usar
        n : int
            numero de peliculas a recomendar
        Returns
        -------
        list
            Lista con los ids de las películas
        """
        res = []
        if 'cooperativo' in recomendadores:
            res.append(self.obtener_recomendacion_cooperativa(user, n))
        if 'contenido' in recomendadores:
            res.append(self.obtener_recomendacion_contenido(user, n))
        if 'demografico' in recomendadores:
            res.append(self.obtener_recomendacion_dg(user, n))
        
        shuffle(res)

        return res

    def get_dg_pref(self) -> np.matrix:
        res = []
        for x in set(self.grupos_demograficos.values()):
            u_dg = [k for k, v in self.grupos_demograficos.items() if v == x]
            scores = self.get_genres_score(u_dg)
            res.append(scores)

        return np.matrix(res)
    
    def get_user_film_rate(self, user, film):
        """Obtiene la puntuacion de una pelicula por un usuario
        Parameters
        ----------
        user : int
            Id del usuario
        film : int
            Id de la pelicula
        Returns
        -------
        int
            Puntuación de la película, o -1 si la película no ha sido puntuada por el usuario
        """
        if len(self.ratings[(self.ratings.movie_id == film) & (self.ratings.user_id == user)]['rating'].tolist()) > 0:
            return self.ratings[(self.ratings.movie_id == film) & (self.ratings.user_id == user)]['rating'].tolist()[0]
        else:
            return -1
    
    def get_film_id(self, film_id):
        film = self.films_df[self.films_df.movie_id == film_id]['title'].tolist()[0].split()
        film_name = ' '.join(film[:-1])
        film_year = film[-1].replace('(', '').replace(')','')
        movie = tmdb.Search().movie(query=film_name, year=film_year)
        if len(movie['results']) == 0: #Buscamos sin año
            movie = tmdb.Search().movie(query=film_name)
        if len(movie['results']) == 0: #Buscamos solo parentesis
            new_name = film_name.split("(")[0]
            movie = tmdb.Search().movie(query=new_name[:-1])

        if len(movie['results']) > 0:
            print(film_name, film_year, movie["results"][0]['id'])
            return movie["results"][0]['id']
        else:
            print("FALLOOOOOOOOOOOOO", film_name, film_year)
            return -1
    
    def tmdb_id(self,movie_id):
        return self.films_df[self.films_df["movie_id"]==movie_id]["tmdb_id"].to_list()[0]
    
    def preprocess_films(self):
        d = []
        for p in self.films_df.movie_id.tolist():
            d.append((p, self.get_film_id(p)))

        res = pd.DataFrame(d, columns=('movie_id', 'tmdb_id'))
        res.to_csv('../data/films.txt',header=None, index=None, sep='\t', mode='w')
        return res
        
    def save_user_neighbours(self, user) -> None:
        if not os.path.exists('../data/usuarios/'+str(user)):
            os.makedirs('../data/usuarios/'+str(user))
        vecinos, vecinos_score = self.obtener_vecinos(self.preferencias_coop, user, self.preferencias_coop.shape[0]-1)
        aux = pd.DataFrame({'vecino':vecinos, 'afinidad':vecinos_score})
        aux.to_csv('../data/usuarios/'+str(user)+'/vecinos.txt', header=None, index=None, sep='\t', mode='w')