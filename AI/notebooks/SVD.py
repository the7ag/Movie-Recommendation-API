import gc
from surprise import Dataset, Reader, SVD
from surprise.model_selection import train_test_split
from surprise.dump import dump, load

class MovieRecommender:
    def __init__(self, df):
        self.df = df

    def prepare_data(self):
        all_movie_ids = self.df['movieId'].unique()
        watched_movies = self.df[self.df['userId'] == 1]['movieId']
        unwatched_movies = [movie_id for movie_id in all_movie_ids if movie_id not in watched_movies]

        reader = Reader(rating_scale=(0.5, 5))
        data = Dataset.load_from_df(self.df[['userId', 'movieId', 'rating']], reader)

        self.trainset, self.testset = train_test_split(data, test_size=0.2, random_state=42)

        del data
        gc.collect()

        self.unwatched_movies = unwatched_movies

    def train_model(self):
        algo = SVD()
        algo.fit(self.trainset)
        self.algo = algo

    def save_model(self, dump_file='trained_model.dump'):
        dump(dump_file, algo=self.algo)

    def load_model(self, dump_file='trained_model.dump'):
        self.loaded_model = load(dump_file)[1]

    def make_recommendations(self, top_n=100):
        predictions = [self.algo.predict(1, movie_id) for movie_id in self.unwatched_movies]
        sorted_predictions = sorted(predictions, key=lambda x: x.est, reverse=True)
        
        print(f"Top {top_n} Recommendations for User 1:")
        for i, pred in enumerate(sorted_predictions[:top_n]):
            movie_id = pred.iid
            movie_rating = pred.est
            print(f"#{i+1}: Movie ID {movie_id}, Predicted Rating: {movie_rating}")

    def evaluate_model(self):
        true_ratings = [rating for (_, _, rating) in self.testset]
        predicted_ratings = [self.algo.predict(uid, iid).est for (uid, iid, _) in self.testset]

        acc = self.accuracy(true_ratings, predicted_ratings)
        print("Accuracy:", acc)

    @staticmethod
    def accuracy(y_true, y_pred, threshold=0.25):
        correct = [abs(true - pred) < threshold for true, pred in zip(y_true, y_pred)]
        return sum(correct) / len(correct)


