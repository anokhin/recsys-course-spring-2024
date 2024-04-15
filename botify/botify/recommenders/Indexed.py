import random
from numpy.random import choice
import numpy as np

from .recommender import Recommender


class IndexedDistr(Recommender):
    def __init__(self, recommendations_redis, catalog, fallback):
        self.recommendations_redis = recommendations_redis
        self.fallback = fallback
        self.catalog = catalog

    def recommend_next(self, user: int, prev_track: int, prev_track_time: float) -> int:
        recommendations = self.recommendations_redis.get(user)

        if recommendations is None:
            return self.fallback.recommend_next(user, prev_track, prev_track_time)

        not_shuffled = list(self.catalog.from_bytes(recommendations))

        if prev_track not in not_shuffled:
            return not_shuffled[0]

        x = random.randrange(len(not_shuffled)+1)
        y = random.randrange(min(x+30, len(not_shuffled)))
        return not_shuffled[y]


class Indexed(Recommender):
    def __init__(self, recommendations_redis, catalog, fallback):
        self.recommendations_redis = recommendations_redis
        self.fallback = fallback
        self.catalog = catalog

    def recommend_next(self, user: int, prev_track: int, prev_track_time: float) -> int:
        recommendations = self.recommendations_redis.get(user)

        if recommendations is not None:
            shuffled = list(self.catalog.from_bytes(recommendations))
            random.shuffle(shuffled)
            return shuffled[0]
        else:
            return self.fallback.recommend_next(user, prev_track, prev_track_time)
