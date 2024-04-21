from data.dataset_utils import DB
from models.content_based_filtering import KNNRecommender
from models.collaborative_filtering import AutoEncoder
from flask import Flask, request
import pandas as pd
import json

url = "postgres://default:I6v0XghdjVAW@ep-nameless-forest-a4upu4jj.us-east-1.aws.neon.tech:5432/verceldb"
app = Flask(__name__)

db = DB(url)
knn = KNNRecommender()
# ae = AutoEncoder()

@app.route('/process-data', methods=['POST'])
def process_data():
    data = request.json
    count = db.get_watch_count(data['id'])
    if count < 5:
        recommendations = db.popular_movies()
    else:
        ratings = db.get_ratings(data['id'])
        recommendations = knn.predict(ratings)
    db.update_recommendations(data['id'], recommendations)
    return recommendations.to_json(orient='records')

if __name__ == '__main__':
    app.run(debug=True, port=5000)