import random

from .recommender import Recommender


class TheBestRecommender(Recommender):
    def __init__(self, recommendations_redis, catalog, fallback):
        self.recommendations_redis = recommendations_redis
        self.catalog = catalog
        self.fallback = fallback

    def recommend_next(self, user: int, prev_track: int, prev_track_time: float) -> int:
        recommendations = self.recommendations_redis.get(user)
        if recommendations is None:
            return self.fallback.recommend_next(user, prev_track, prev_track_time)
        recommendations = list(self.catalog.from_bytes(recommendations))
        if prev_track not in recommendations:
            return recommendations[0]
        index = recommendations.index(prev_track)
        return recommendations[(index + 1) % len(recommendations)]
