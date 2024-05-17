from data.dataset_utils import DB
from models.content_based_filtering import KNNRecommender
from models.collaborative_filtering import AutoEncoder
from flask import Flask, request
import pandas as pd
import json


db1 = None
db2 = None
def connect_databases():
    global db1, db2
    db1 = DB( # All Tables Except The Ratings
        dbname="vercel_db_35rb",
        user="vercel_db_35rb_user",
        password="dSYKqdUoLtuKhljWHsE4I0lcl29UxIni",
        host="dpg-coku3qud3nmc739lls40-a.oregon-postgres.render.com",
        port="5432"
    )

    db2 = DB( # Ratings Table
        dbname="recommendation_cbnm",
        user="recommendation_cbnm_user",
        password="E9zEBx0r87RKMbzl1uqxaPbp67EG9gwC",
        host="dpg-coklt16n7f5s738tii3g-a.oregon-postgres.render.com",
        port="5432"
    )

connect_databases()
app = Flask(__name__)
knn = KNNRecommender()
ae = AutoEncoder()

@app.route('/process-data', methods=['POST'])
def process_data():
    data = request.json
    if data is None or 'id' not in data:
        return json.dumps({'error': 'No id provided'})
    
    if not db1.check_connection() or not db2.check_connection():
        connect_databases()
                 
    if not db1.check_user(data['id']):
        return json.dumps({'error': 'User not found'})
    
    count1 = db1.get_watch_count(data['id'])
    count2 = db2.get_watch_count(data['id'])
    count = count1 + count2
    print(f"\nuser {data['id']} watched {count} movies")
    if count == 0:
        recommendations = db2.popular_movies()
    elif count < 5:
        ratings1 = db1.get_ratings(data['id'])
        ratings2 = db2.get_ratings(data['id'])
        ratings = pd.concat([ratings1, ratings2])
        recommendations = db2.popular_movies(movieids=ratings['movieid'])
    else:    
        ratings1 = db1.get_ratings(data['id'])
        ratings2 = db2.get_ratings(data['id'])
        ratings = pd.concat([ratings1, ratings2])
        print(f"\nuser {data['id']} watched movies:")
        print(db1.get_movie_titles(ratings['movieid']))
        
        if not knn.check(ratings['movieid']):
            print("\nRetraining KNN...")
            knn.train(db1.get_table('movies'))
        
        print("\nSearching Using Content Based Filtering...")
        recommendations = knn.predict(ratings)
                        
        if ae.check(data['id'], recommendations):
            print("\nSorting Using Collabritive Filtering...")
            recommendations = ae.sort(data['id'], recommendations)
        else:
            recommendations = recommendations[:10]
        
    print(f"\nuser {data['id']} recommended movies:")
    print(db1.get_movie_titles(recommendations))
    db1.update_recommendations(data['id'], recommendations)
    return json.dumps({'recommendations': recommendations})

if __name__ == '__main__':
    app.run()