import random

import numpy as np

from .recommender import Recommender


class IndexedSampling(Recommender):
    def __init__(self, recommendations_redis, catalog, fallback):
        self.recommendations_redis = recommendations_redis
        self.fallback = fallback
        self.catalog = catalog

    def recommend_next(self, user: int, prev_track: int, prev_track_time: float) -> int:
        recommendations = self.recommendations_redis.get(user)

        if recommendations is not None:
            recs = list(self.catalog.from_bytes(recommendations))
            try:
                cur_index = (recs.index(prev_track) + 1) % len(recs)
            except ValueError:
                cur_index = 0

            return recs[cur_index]
        else:
            return self.fallback.recommend_next(user, prev_track, prev_track_time)
