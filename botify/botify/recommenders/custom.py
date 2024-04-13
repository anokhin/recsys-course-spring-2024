import random

from .recommender import Recommender


class Custom(Recommender):
    def __init__(self, recommendations_redis, catalog, fallback):
        self.recommendations_redis = recommendations_redis
        self.fallback = fallback
        self.catalog = catalog

    def recommend_next(self, user: int, prev_track: int, prev_track_time: float) -> int:
        recommendations = self.recommendations_redis.get(user)

        if recommendations is not None:
            lst = list(self.catalog.from_bytes(recommendations))

            if prev_track in lst:
                positivity = prev_track_time >= 0.77

                if positivity:
                    return lst[(lst.index(prev_track) + 1) % len(lst)]
                return lst[(lst.index(prev_track) + 2) % len(lst)]

            return lst[0]

        return self.fallback.recommend_next(user, prev_track, prev_track_time)
