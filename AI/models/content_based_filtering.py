import joblib
import pandas as pd
from scipy.sparse import hstack
from sklearn.neighbors import NearestNeighbors
from sklearn.feature_extraction.text import CountVectorizer


class KNNRecommender:
    def __init__(self):
        pass