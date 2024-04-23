from flask import Flask, request
import psycopg2
import pandas as pd
from joblib import load
from scipy.sparse import load_npz

knn_model = load(r'C:\Users\hadyh\OneDrive\Desktop\server\DB_CRUD_OP-main\API\knn_model.joblib')
movies = pd.read_csv(r'C:\Users\hadyh\OneDrive\Desktop\server\DB_CRUD_OP-main\API\movies.csv')
combined_matrix =  load_npz(r'C:\Users\hadyh\OneDrive\Desktop\server\DB_CRUD_OP-main\API\combined_matrix.npz')
url = "postgres://default:I6v0XghdjVAW@ep-nameless-forest-a4upu4jj.us-east-1.aws.neon.tech:5432/verceldb"
movies_num = 5


def get_recommendations(movie_titles):
    movie_indices = []
    for title in movie_titles:
        idx = movies[movies['title'] == title].index[0]
        movie_indices.append(idx)
    distances, indices = knn_model.kneighbors(combined_matrix[movie_indices])
    similar_movies_indices = indices.flatten()
    similar_movies_indices = similar_movies_indices[~pd.Series(similar_movies_indices).isin(movie_indices)]  # Exclude input movies
    return movies.iloc[similar_movies_indices]['title']

app = Flask(__name__)

@app.route('/process-data', methods=['POST'])
def process_data():
    data = request.json
    # Process the received data
    conn = psycopg2.connect(
    dbname="postgres",
    user="postgres",
    password="3011",
    host="localhost",
    port="5432"
    )
    cursor = conn.cursor()
    cursor.execute("SELECT movieid FROM ratings WHERE userid = %s ORDER BY rating DESC LIMIT 5;", (str(data['id']),))


    # Fetch all the rows
    top_movie_ids = cursor.fetchall()
    if len(top_movie_ids) == movies_num:
        print('Ok you know your movies')
        # Fetch the titles for the top rated movies
        top_movies = []
        for movie_id in top_movie_ids:
            conn2 = psycopg2.connect(url)
            cursor2 = conn2.cursor()
            cursor2.execute("SELECT title FROM movies WHERE movieid = %s;", (movie_id,))
            title = cursor2.fetchone()[0]
            top_movies.append(title)
        recommendations = get_recommendations(top_movies)
        # Convert Pandas Series to Python list
        recommendations_list = recommendations.tolist()
        print(f'Top 5 Movies : {top_movies[:5]}')
        print('-'*20)
        print(f'Recommendations Based on Top 5 Movies : \n{recommendations_list[:5]}')

    # Execute SQL query with the Python list
        cursor.execute("UPDATE users SET recommendations = %s WHERE userid = %s;", (recommendations_list, str(data['id']),))
        conn.commit()
    elif len(top_movie_ids) < movies_num:
        print('Check These Sick Movies')
        cursor.execute("""
                    SELECT movieid, count(rating) AS avg_rating FROM ratings 
                    GROUP BY movieid 
                    ORDER BY avg_rating DESC 
                    LIMIT 10;
                    """)
        movies_data = cursor.fetchall()

# Extracting movieids from fetched data
        movies_ids = [row[0] for row in movies_data]
        highest = []
        for movie_id in movies_ids:
            conn2 = psycopg2.connect(url)
            cursor2 = conn2.cursor()            
            cursor2.execute("SELECT title FROM movies WHERE movieid = %s;", (movie_id,))
            title = cursor2.fetchone()[0]
            highest.append(title)
        print(f'Top Movies : {highest[:movies_num]}')


    cursor.close()
    conn.close()
    processed_data = {"message": "Data processed successfully"}
    return processed_data

if __name__ == '__main__':
    app.run(debug=True, port=5000)
