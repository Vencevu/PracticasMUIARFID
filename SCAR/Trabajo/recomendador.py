import random
import re
from os import sep

import numpy as np
import pandas as pd
import requests
import tmdbsimple as tmdb
from scipy.stats.stats import pearsonr
from surprise import SVD, Dataset, KNNBasic, Reader
from surprise.model_selection import cross_validate
from collections import defaultdict

tmdb.REQUESTS_SESSION = requests.Session()
tmdb.API_KEY = '1e11e7d4c5f3aad6e459fc0f63bfb0f5'
tmdb.REQUESTS_TIMEOUT = 5

# Generos
generos = pd.read_csv("../data/genre.txt", names=["genre_id", "genre_name"], sep="\t")
# Usuarios
users_df = pd.read_csv(
    "../data/users.txt", names=["user_id", "age", "gender", "occupation"], sep="\t"
)
# Peliculas
all_genre = generos.genre_name.values.tolist()
all_genre = ["movie_id"] + all_genre + ["title"]
films = []
films_df = pd.read_csv("../data/items.txt",encoding="iso-8859-1" ,names=all_genre, sep="\t")
# Valoraciones
ratings = pd.read_csv(
    "../data/u1_base.txt", names=["user_id", "movie_id", "rating"], sep="\t"
)
ratings = ratings.merge(users_df, on="user_id")

for film in films_df["title"].tolist():
    years = re.findall(r'(\d{4})', film)
    year = years[0] if len(years) > 0 else 0
    film = re.sub(r'\(\d{4}\)', '', film)
    films.append((film, year))