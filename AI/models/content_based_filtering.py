import joblib
import pandas as pd
from scipy.sparse import hstack
from sklearn.neighbors import NearestNeighbors
from sklearn.feature_extraction.text import CountVectorizer


class KNNRecommender:
    def __init__(self):
        self.features = joblib.load('knn_features.dump')
        self.knn = NearestNeighbors(n_neighbors=10, metric='euclidean')
        self.knn.fit(self.features)
        self.movieid_map = pd.read_csv('../data/movieids.csv', index_col='index')


    def _format(features):
        features = features.replace('{', '').replace('}', '').replace('"', '').split(',')
        features = [f.replace(' ', '') for f in features]
        return ' '.join(features)


    def train(self, movies):      
        movies['cast'].fillna('unknown', inplace=True)
        movies['genres'].fillna('other', inplace=True)
        movies['genres'] = movies['genres'].apply(self._format)
        movies['cast'] = movies['cast'].apply(self._format)
        movieid_map = movies[['movieid']].reset_index()
        movieid_map.to_csv('../data/movieids.csv', index=False)
        
        vectorizer = CountVectorizer()
        title = vectorizer.fit_transform(movies['title'])
        genres = vectorizer.fit_transform(movies['genres'])
        cast = vectorizer.fit_transform(movies['cast'])
        features = hstack([title, genres, cast])
        joblib.dump(features, 'knn_features.dump')
    
    
    def predict(self, ratings):
        movieids = self.movieid_map[self.movieid_map['movieid'].isin(ratings['movieid'])]['index']
        moviedict = {}
        for movieid in movieids:
            features = self.features[movieid]
            distances, indices = self.knn.kneighbors(features)
            indices = indices.flatten()
            distances = distances.flatten()
            distances = distances / (ratings[ratings['movieid'] == \
                self.movieid_map.loc[movieid, 'movieid']]['rating'].values[0])**2
            
            for index, distance in zip(indices, distances):
                if index in moviedict:
                    moviedict[index] = min(moviedict[index], distance)
                else:
                    moviedict[index] = distance
        
        moviedict = dict(sorted(moviedict.items(), key=lambda item: item[1]))
        recs = self.movieid_map[self.movieid_map['index'].isin(moviedict.keys())]['movieid']
        recs = recs[~recs.isin(ratings['movieid'])]
        recs = recs.tolist()[:10]
        return recs