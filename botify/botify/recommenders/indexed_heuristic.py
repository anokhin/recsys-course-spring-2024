import random

from .recommender import Recommender


class Indexed_Heuristic(Recommender):
    def __init__(self, recommendations_redis, catalog, fallback):
        self.recommendations_redis = recommendations_redis
        self.fallback = fallback
        self.catalog = catalog

    def recommend_next(self, user: int, prev_track: int, prev_track_time: float) -> int:
        recommendations = self.recommendations_redis.get(user)

        if recommendations is not None:
            recommendations = list(self.catalog.from_bytes(recommendations))
            if prev_track not in recommendations or prev_track_time <  0.5:
                next_track = random.choice(recommendations)
            else:
                idx = (recommendations.index(prev_track) + 1) % len(recommendations)
                next_track = recommendations[idx]
            
            return next_track
        else:
            return self.fallback.recommend_next(user, prev_track, prev_track_time)
