import pandas as pd
import psycopg2

class DB:
    def __init__(self, *args, **kwargs):
        self.conn = psycopg2.connect(*args, **kwargs)
        self.cursor = self.conn.cursor()
    
    def get_ratings(self, user_id):
        self.cursor.execute("SELECT movieid, rating FROM ratings WHERE userid = %s;", (str(user_id),))
        ratings = pd.DataFrame(self.cursor.fetchall(), columns=['movieid', 'rating'])
        ratings['movieid'] = ratings['movieid'].astype(str)
        return ratings
    
    def popular_movies(self, n=10):
        self.cursor.execute("""
            SELECT movieid, count(rating) * avg(rating) * avg(rating) AS score
            FROM ratings
            GROUP BY movieid
            ORDER BY score DESC
            LIMIT %s;
            """, (n,))
        popular_movies = pd.DataFrame(self.cursor.fetchall(), columns=['movieid', 'score'])
        popular_movies['movieid'] = popular_movies['movieid'].astype(str)
        popular_movies = popular_movies.drop(columns=['score'])
        return popular_movies
    
    def get_watch_count(self, user_id):
        self.cursor.execute("SELECT count(rating) FROM ratings WHERE userid = %s;", (str(user_id),))
        count = self.cursor.fetchone()[0]
        return count

    def get_movie_titles(self, movie_ids):
        self.cursor.execute("SELECT movieid, title FROM movies WHERE movieid = ANY(%s);", (movie_ids,))
        movie_titles = pd.DataFrame(self.cursor.fetchall(), columns=['movieid', 'title'])
        movie_titles['movieid'] = movie_titles['movieid'].astype(str)
        return movie_titles
    
    def get_all_userids(self):
        self.cursor.execute("SELECT DISTINCT userid FROM users;")
        userids = pd.DataFrame(self.cursor.fetchall(), columns=['userid'])
        userids['userid'] = userids['userid'].astype(str)
        return userids
    
    def get_all_movieids(self):
        self.cursor.execute("SELECT DISTINCT movieid FROM movies;")
        movieids = pd.DataFrame(self.cursor.fetchall(), columns=['movieid'])
        movieids['movieid'] = movieids['movieid'].astype(str)
        return movieids
    
    def update_recommendations(self, user_id, recommendations):
        recommendations_tuples = [tuple(x) for x in recommendations.values]
        self.cursor.execute("UPDATE users SET recommendation = %s WHERE userid = %s;", (recommendations_tuples, str(user_id),))
        self.conn.commit()
    
    def close(self):
        self.cursor.close()
        self.conn.close()