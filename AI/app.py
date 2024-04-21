from data.dataset_utils import DB
from models.content_based_filtering import KNNRecommender
# from models.collaborative_filtering import AutoEncoder
from flask import Flask, request
import pandas as pd
import json

url1 = "postgres://default:I6v0XghdjVAW@ep-nameless-forest-a4upu4jj.us-east-1.aws.neon.tech:5432/verceldb"
url2 = "postgres://postgres:3011@localhost:5432/postgres"

app = Flask(__name__)

db1 = DB(url1)
db2 = DB(url2)

knn = KNNRecommender()
# ae = AutoEncoder()

@app.route('/process-data', methods=['POST'])
def process_data():
    data = request.json
    count = db2.get_watch_count(data['id'])
    if count < 5:
        recommendations = db2.popular_movies()
    else:
        ratings = db2.get_ratings(data['id'])
        recommendations = knn.predict(ratings)
        
    db1.update_recommendations(data['id'], recommendations)
    return recommendations.to_json(orient='records')

if __name__ == '__main__':
    app.run(debug=True, port=5000)