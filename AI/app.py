from data.dataset_utils import DB
from models.content_based_filtering import KNNRecommender
from models.collaborative_filtering import AutoEncoder
from flask import Flask, request
import pandas as pd
import json

url = "postgres://default:I6v0XghdjVAW@ep-nameless-forest-a4upu4jj.us-east-1.aws.neon.tech:5432/verceldb"
# db_online = DB(url)

db_offline = DB(
    dbname="postgres",
    user="postgres",
    password="root",
    host="localhost",
    port="5432"
)

app = Flask(__name__)
knn = KNNRecommender()
ae = AutoEncoder()

@app.route('/process-data', methods=['POST'])
def process_data():
    data = request.json
    if data is None: return json.dumps({'error': 'No data provided'})
    
    count = db_offline.get_watch_count(data['id'])
    if count < 5:
        recommendations = db_offline.popular_movies()
    else:
        ratings = db_offline.get_ratings(data['id'])
        print(f"\nuser {data['id']} watched movies:")
        print(db_offline.get_movie_titles(ratings['movieid']))
        
        if not knn.check(ratings['movieid']):
            print("\nRetraining KNN...")
            knn.train(db_offline.get_table('movies'))
        
        print("\nSearching Using Content Based Filtering...")
        recommendations = knn.predict(ratings)
                        
        if ae.check(data['id'], recommendations):
            print("\nSorting Using Collabritive Filtering...")
            recommendations = ae.sort(data['id'], recommendations)
            
    
    print(f"\nuser {data['id']} recommended movies:")
    print(db_offline.get_movie_titles(recommendations))
    # db_online.update_recommendations(data['id'], recommendations)
    db_offline.update_recommendations(data['id'], recommendations)
    return json.dumps({'recommendations': recommendations})

if __name__ == '__main__':
    app.run(debug=True, port=5000)