from data.dataset_utils import DB
from models.content_based_filtering import KNNRecommender
from models.collaborative_filtering import AutoEncoder
from flask import Flask, request
import pandas as pd
import json

url = "postgres://default:I6v0XghdjVAW@ep-nameless-forest-a4upu4jj.us-east-1.aws.neon.tech:5432/verceldb"
db1 = DB(url)

db2 = DB(
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
    
    count = db2.get_watch_count(data['id'])
    if count < 5:
        recommendations = db2.popular_movies()
    else:
        ratings = db2.get_ratings(data['id'])
        print(db1.get_movie_titles(ratings['movieid'])) # Debugging
        
        if not knn.check(ratings['movieid']):
            knn.train(db1.get_all_movieids())
        recommendations = knn.predict(ratings)
        
        if ae.check(data['id'], ratings['movieid']):
            recommendations = ae.sort(data['id'], recommendations)
        
    print(db1.get_movie_titles(recommendations)) # Debugging
    db1.update_recommendations(data['id'], recommendations)
    db2.update_recommendations(data['id'], recommendations)
    return json.dumps({'recommendations': recommendations})

if __name__ == '__main__':
    app.run(debug=True, port=5000)