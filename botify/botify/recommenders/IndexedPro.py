import random

from .recommender import Recommender


class IndexedPro(Recommender):
    def __init__(self, recommendations_redis, catalog, fallback):
        self.recommendations_redis = recommendations_redis
        self.fallback = fallback
        self.catalog = catalog

    def recommend_next(self, user: int, prev_track: int, prev_track_time: float) -> int:
        recommendations = self.recommendations_redis.get(user)

        if recommendations is not None:
            recommendations = list(self.catalog.from_bytes(recommendations))
            if ((prev_track in recommendations) and (prev_track_time > 0.9) and
                    (recommendations.index(prev_track) < (len(recommendations) - 1))):
                return recommendations[recommendations.index(prev_track) + 1]
            random.shuffle(recommendations)
            return recommendations[0]

        else:
            return self.fallback.recommend_next(user, prev_track, prev_track_time)
