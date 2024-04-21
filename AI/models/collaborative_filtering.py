import pandas as pd
from surprise import Dataset, Reader, SVD, accuracy
from surprise import dump, load
from surprise.model_selection import train_test_split


class SVDRecommender:
    def __init__(self):
        pass