import random

import numpy as np

from .recommender import Recommender


class TheBestRecommender(Recommender):
    def __init__(self, recommendations_redis, catalog, fallback):
        self.recommendations_redis = recommendations_redis
        self.catalog = catalog
        self.fallback = fallback
        self.last_track_time_size = 5
        self.last_track_time = np.ones(self.last_track_time_size)

    def recommend_next(self, user: int, prev_track: int, prev_track_time: float) -> int:
        recommendations = self.recommendations_redis.get(user)
        if recommendations is None:
            return self.fallback.recommend_next(user, prev_track, prev_track_time)
        recommendations = list(self.catalog.from_bytes(recommendations))
        if prev_track not in recommendations:
            return recommendations[0]
        index = recommendations.index(prev_track)
        for i in range(self.last_track_time_size - 1):
            self.last_track_time[i] = self.last_track_time[i + 1]
        self.last_track_time[-1] = prev_track_time
        if np.all(np.vectorize(lambda x: x < 0.11)(self.last_track_time)): # 0.1 not bad
            return self.fallback.recommend_next(user, prev_track, prev_track_time)
        if prev_track_time < 0.3 and index > 5:
            return recommendations[0]
        return recommendations[(index + 1) % len(recommendations)]
