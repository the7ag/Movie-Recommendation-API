import os
import numpy as np
import pandas as pd
import tensorflow as tf
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'


class AutoEncoder:
    def __init__(self):
        self.dir_path = os.path.dirname(os.path.realpath(__file__))
        self.model_path = os.path.join(self.dir_path, '../data/AutoEncoder/ae_model.keras')
        self.movieid_path = os.path.join(self.dir_path, '../data/AutoEncoder/ae_movieids.csv')
        self.userid_path = os.path.join(self.dir_path, '../data/AutoEncoder/ae_userids.csv')
        
        self.model = tf.keras.models.load_model(self.model_path)
        self.movieid_map = pd.read_csv(self.movieid_path)
        self.userid_map = pd.read_csv(self.userid_path)
        
    def check(self, userid, movieids):
        df = pd.DataFrame()
        df['movieid'] = movieids
        return (userid in self.userid_map['userid']) and all(df['movieid'].isin(self.movieid_map['movieid']))
    
    def train(self, ratings):
        # load data
        users = ratings['userid'].values
        movies = ratings['movieid'].values
        ratings = ratings['rating'].values
        classes = (ratings - 1).astype(np.int8)
        
        # map userids and movieids
        userids = pd.Series(users).unique()
        movieids = pd.Series(movies).unique()
        userids = pd.Series(userids).reset_index()
        movieids = pd.Series(movieids).reset_index()
        userids.to_csv(self.userid_path, index=False)
        movieids.to_csv(self.movieid_path, index=False)
        
        # create model
        tf.keras.backend.clear_session()
        user_input = tf.keras.layers.Input(shape=(1,), name='user_input')
        movie_input = tf.keras.layers.Input(shape=(1,), name='movie_input')

        user_embedding = tf.keras.layers.Embedding(input_dim=len(self.userid_map), output_dim=32, name='user_embedding')(user_input)
        movie_embedding = tf.keras.layers.Embedding(input_dim=len(self.movieid_map), output_dim=32, name='movie_embedding')(movie_input)
        concat = tf.keras.layers.Concatenate(name='concat')([tf.keras.layers.Flatten()(user_embedding), tf.keras.layers.Flatten()(movie_embedding)])
        concat = tf.keras.layers.Dropout(0.5, name='dropout_1')(concat)

        dense = tf.keras.layers.Dense(128, activation='relu', name='dense_1')(concat)
        dense = tf.keras.layers.Dropout(0.5, name='dropout_2')(dense)
        dense = tf.keras.layers.Dense(64, activation='relu', name='dense_2')(dense)

        output_layer = tf.keras.layers.Dense(10, activation='softmax', name='output_layer')(dense)
        model = tf.keras.Model(inputs=[user_input, movie_input], outputs=output_layer)
        model.compile(optimizer='SGD', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
        model.fit([users, movies], classes, epochs=10, batch_size=1024)
        model.save(self.model_path)
        
        
    def smooth_score(self, prediction):
        return np.sum(prediction * np.arange(1, 11))
    
    def sort(self, userid, movieids):
        userid = self.userid_map[self.userid_map['userid'] == userid]['index'].values[0]
        movieids = self.movieid_map[self.movieid_map['movieid'].isin(movieids)]['index']
        predictions = []
        for movieid in movieids:
            prediction = self.model.predict([np.array([userid]), np.array([movieid])])
            prediction = self.smooth_score(prediction)
            predictions.append((movieid, prediction))
        
        predictions = sorted(predictions, key=lambda x: x[1])
        sorted_movieids = [movieid for movieid, _ in predictions]
        return sorted_movieids