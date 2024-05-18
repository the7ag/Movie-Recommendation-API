import os
import joblib
import numpy as np
import pandas as pd
from scipy.sparse import hstack
from sklearn.neighbors import NearestNeighbors
from sklearn.feature_extraction.text import CountVectorizer


class KNNRecommender:
    def __init__(self):
        self.dir_path = os.path.dirname(os.path.realpath(__file__))
        self.knn_path = os.path.join(self.dir_path, '../data/KNN/knn_features.dump')
        self.movieid_path = os.path.join(self.dir_path, '../data/KNN/knn_movieids.csv')
        
        self.features = joblib.load(self.knn_path)
        self.knn = NearestNeighbors(n_neighbors=10, metric='euclidean')
        self.knn.fit(self.features)
        self.movieid_map = pd.read_csv(self.movieid_path)
        self.movieid_map['movieid'] = self.movieid_map['movieid'].astype(str)
        

    def _format(self, features):
        # features = features.replace('{', '').replace('}', '').replace('[', '')\
        # .replace(']', '').replace('"', '').replace("'", '').split(',')
        features = [f.replace(' ', '') for f in features]
        return ' '.join(features)
    
    def check(self, movieids):
        return movieids.isin(self.movieid_map['movieid']).all()

    def train(self, movies):
        movies['cast'].fillna('unknown', inplace=True)
        movies['genres'].fillna('other', inplace=True)
        movies['genres'] = movies['genres'].apply(self._format)
        movies['cast'] = movies['cast'].apply(self._format)
        movieid_map = movies[['movieid']].reset_index()
        movieid_map.to_csv(self.movieid_path, index=False)
        
        vectorizer = CountVectorizer()
        title = vectorizer.fit_transform(movies['title'])
        genres = vectorizer.fit_transform(movies['genres'])
        cast = vectorizer.fit_transform(movies['cast'])
        features = hstack([title, genres, cast])
        joblib.dump(features, self.knn_path)
    
    def predict(self, ratings):
        movieids = self.movieid_map[self.movieid_map['movieid'].isin(ratings['movieid'])]['index']
        moviedict = np.inf * np.ones(self.features.shape[0])
        features = self.features[movieids]
        distances, indices = self.knn.kneighbors(features)
        distances = distances / np.array(ratings['rating'])[:, np.newaxis]**2
        for dist_row, idx_row in zip(distances, indices):
            moviedict[idx_row] = np.minimum(moviedict[idx_row], dist_row)
        recs = np.argsort(moviedict)
        recs = self.movieid_map.loc[recs, 'movieid']
        recs = recs[~recs.isin(ratings['movieid'])].tolist()
        return recs[:20]