import random
import re
from os import sep

import numpy as np
import pandas as pd
import requests
import tmdbsimple as tmdb
from scipy.stats import pearsonr
from surprise import SVD, Dataset, KNNBasic, Reader
from surprise.model_selection import cross_validate
from collections import defaultdict, Counter
from itertools import islice
import collections

tmdb.REQUESTS_SESSION = requests.Session()
tmdb.API_KEY = '1e11e7d4c5f3aad6e459fc0f63bfb0f5'
tmdb.REQUESTS_TIMEOUT = 5

class Recomendador():
    def __init__(self, data_path) -> None:
        self.preferencias = []
        self.pref_hyb = []
        self.pref_dg = []
        self.grupos_demograficos = {}
        self.users_df = pd.read_csv(data_path, names=["user_id", "age", "gender", "occupation"], sep="\t")
        self.ratings = pd.read_csv("data/u1_base.txt", names=["user_id", "movie_id", "rating"], sep="\t")
        self.generos = pd.read_csv("data/genre.txt", names=["genre_id", "genre_name"], sep="\t")

        all_genre = self.generos.genre_name.values.tolist()
        all_genre = ["movie_id"] + all_genre + ["title"]
        self.films_df = pd.read_csv("data/items.txt",encoding="iso-8859-1" ,names=all_genre, sep="\t")

    def take(n, iterable):
        res = {}
        i = 0
        for k, v in iterable.items():
            if i >= n:
                break
            res[k] = v
            i += 1
            
        return res
    
    def get_hyb_pref(self):
        pref_hyb = []
        for u in self.ratings.user_id.unique().tolist():
            pref = np.round(np.sum(np.matrix([self.preferencias['a'][u-1], self.pref_dg['a'][self.grupos_demograficos[u]-1]]), axis=0)/2, 0).tolist()[0]
            pref_hyb.append(pref)

        pref_hyb = np.matrix(pref_hyb)

    def load_grupos_demograficos(self):
        self.grupos_demograficos = {}
        for user_id in self.users_df.user_id.unique().tolist():
            user = self.users_df[self.users_df.user_id == user_id]
            user_demo_group = self.get_user_type(user.gender.tolist()[0], user.age.tolist()[0], user.occupation.tolist()[0])
            self.grupos_demograficos[user_id] = user_demo_group

    def get_pref(self):
        res = []
        for u in self.ratings.user_id.unique().tolist():
            best_genres = []
            for i in self.generos['genre_name'].tolist():
                puntos = self.genre_seen(self.films_df, self.ratings, u, i)
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
                    pref.append(1)
                else:
                    pref.append(0)

            res.append(pref)

        return res
    
    def load_preferencias(self, path="", path_dg="", path_hyb=""):
        self.preferencias = np.load(path)['a'] if path != "" else self.get_pref()
        self.pref_dg = np.load(path_dg)['a'] if path_dg != "" else self.get_dg_pref()
        self.pref_hyb = np.load(path_hyb)['a'] if path_hyb != "" else self.get_hyb_pref()
            

    def movie_votes_demographic(self, grupos, movie_id, grupo):
        usuarios = [k for k, v in grupos.items() if v == grupo]
        return len(self.ratings[(self.ratings.user_id.isin(usuarios)) & (self.ratings.movie_id == movie_id)].index), self.ratings[(self.ratings.user_id.isin(usuarios)) & (self.ratings.movie_id == movie_id)].mean()['rating'], self.ratings[self.ratings.movie_id == movie_id].mean()['rating']

    def genre_seen(self, user_id, genre_name):
        scores = []
        for film_id in self.ratings[self.ratings['user_id'] == user_id].movie_id.tolist():
            if self.films_df[self.films_df['movie_id'] == film_id][genre_name].tolist()[0] == 1:
                scores.append(self.ratings[(self.ratings['movie_id'] == film_id) & (self.ratings['user_id'] == user_id)]['rating'].tolist()[0])

        return sum(scores)/len(scores) if scores != [] else 0

    def get_genres_score(self, users):
        best_genres = {}
        for u in users:
            for i in self.generos['genre_name'].tolist():
                puntos = self.genre_seen(self.films_df, self.ratings, u, i)
                if puntos > 2.5:
                    if i not in best_genres.keys():
                        best_genres[i] = puntos/len(users)
                    else:
                        best_genres[i] += puntos/len(users)

        best_genres = {k: v for k, v in sorted(best_genres.items(), key=lambda item: item[1])}
        best_genres = self.take(6, best_genres)

        pref = []

        for genero in self.generos['genre_name'].tolist():
            add = False
            for k, v in best_genres.items():
                if genero == k:
                    add = True
                    break
            if add:
                pref.append(1)
            else:
                pref.append(0)

        return pref

    def obtener_vecinos(preferencias, user, k=1):
        vecinos = [0]*k
        vecinos_score = [0]*k
        pref = preferencias[user]
        for i in range(0, preferencias.shape[0]):
            if i == user:
                continue
            pref_comp = np.matrix([pref, preferencias[i]])
            score = sum([1 if pref_comp[0,j] == pref_comp[1,j] else 0 for j in range(0, pref_comp.shape[1])])
            if score > min(vecinos_score):
                vecinos[vecinos_score.index(min(vecinos_score))] = i + 1
                vecinos_score[vecinos_score.index(min(vecinos_score))] = score
                
                
        return vecinos, vecinos_score

    def obtener_recomendacion(self, user):
        vecino = self.obtener_vecinos(self.preferencias, 0, 1)
        pelis_user = self.ratings[self.ratings.user_id == user]['movie_id'].tolist()
        pelis_vecino = self.ratings[self.ratings.user_id == vecino[0][0]][['movie_id', 'rating']].sort_values(by=['rating'], ascending=False)['movie_id'].tolist()
        return [x for x in pelis_vecino if x not in pelis_user][:5]

    def get_dg_pref(self):
        res = []
        for x in set(self.grupos_demograficos.values()):
            u_dg = [k for k, v in self.grupos_demograficos.items() if v == x]
            scores = self.get_genres_score(u_dg, self.generos, self.films_df, self.ratings)
            res.append(scores)

        return np.matrix(res)

    def get_user_type(self, gender, age, occupation):
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