import pandas as pd
import numpy as np
import psycopg2


class DB:
    def __init__(self, *args, **kwargs):
        self.conn = psycopg2.connect(*args, **kwargs)
        self.cursor = self.conn.cursor()
        
    def check_connection(self):
        try:
            self.cursor.execute("SELECT 1;")
            result = self.cursor.fetchone()
            return bool(result) if result else False
        except Exception as e:
            print(f"Error checking connection: {e}")
            return False

    def check_user(self, user_id):
        try:
            self.cursor.execute("SELECT 1 FROM users WHERE userid = %s;", (str(user_id),))
            result = self.cursor.fetchone()
            return bool(result) if result else False
        except Exception as e:
            print(f"Error checking user: {e}")
            return False
    
    def get_ratings(self, user_id):
        self.cursor.execute("SELECT movieid, rating FROM ratings WHERE userid = %s;", (str(user_id),))
        ratings = pd.DataFrame(self.cursor.fetchall(), columns=['movieid', 'rating'])
        ratings['movieid'] = ratings['movieid'].astype(str)
        return ratings
    
    # def popular_movies(self, n=10):
    #     self.cursor.execute("""
    #         SELECT movieid, count(rating) * avg(rating) * avg(rating) AS score
    #         FROM ratings
    #         GROUP BY movieid
    #         ORDER BY score DESC
    #         LIMIT %s;
    #         """, (n,))
    #     popular_movies = pd.DataFrame(self.cursor.fetchall(), columns=['movieid', 'score'])
    #     popular_movies = popular_movies['movieid'].astype(str).tolist()
    #     return popular_movies
    
    def popular_movies(self, n=10):
        hard_coded_movies = ['318', '296', '356', '2571', '593', '260', '2959',
                             '527','858', '1196', '4993', '50', '7153', '1198',
                             '5952', '1210', '110', '2858', '1', '58559', '79132',
                             '480', '589', '47', '1270', '608', '2028', '457', '2762',
                             '3578', '4226', '150', '1704', '32', '1193', '1197', '1221',
                             '4306', '1136', '541', '364', '1291', '7361', '1213', '588',
                             '4973', '1214', '1089', '590', '6539']
        
        random_indices = np.random.choice(len(hard_coded_movies), n, replace=False)
        random_indices.sort()
        hard_coded_movies = [hard_coded_movies[i] for i in random_indices]
        return hard_coded_movies

    def get_watch_count(self, user_id):
        try:
            self.cursor.execute("SELECT COUNT(rating) FROM ratings WHERE userid = %s;", (str(user_id),))
            result = self.cursor.fetchone()
            return result[0] if result else 0
        except Exception as e:
            print(f"Error getting watch count: {e}")
            return 0

    def get_movie_titles(self, movie_ids):
        movie_ids = [str(x) for x in movie_ids]
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
    
    def get_table(self, table):
        self.cursor.execute(f"SELECT * FROM {table};")
        table = pd.DataFrame(self.cursor.fetchall(), columns=[desc[0] for desc in self.cursor.description])
        return table
    
    def update_recommendations(self, user_id, recommendations):
        string = "{\"" + '\",\"'.join(recommendations) +"\"}"
        self.cursor.execute("UPDATE users SET recommendation = %s WHERE userid = %s;", (string, str(user_id),))
        self.conn.commit()
    
    def close(self):
        self.cursor.close()
        self.conn.close()