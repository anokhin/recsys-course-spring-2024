import random

from .recommender import Recommender


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

class MYIndexed(Recommender):

    def __init__(self, recommendations_redis, catalog, fallback):
        self.recommendations_redis = recommendations_redis
        self.fallback = fallback
        self.catalog = catalog


    def recommend_next(self, user: int, prev_track: int, prev_track_time: float) -> int:
        recommendations = self.recommendations_redis.get(user)
        if recommendations is None:
            return self.fallback.recommend_next(user, prev_track, prev_track_time)

        recommendations = list(self.catalog.from_bytes(recommendations))
        n = len(recommendations)
        for ind, recommendation in enumerate(recommendations):
            if recommendation == prev_track:
                return recommendations[(ind + 1) % n]
            
        return recommendations[0]
