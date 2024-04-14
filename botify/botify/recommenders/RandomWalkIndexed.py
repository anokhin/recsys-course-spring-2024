import numpy as np

from .recommender import Recommender


class RandomWalkIndexed(Recommender):
    def __init__(self, recommendations_redis, catalog, fallback):
        self.recommendations_redis = recommendations_redis
        self.fallback = fallback
        self.catalog = catalog

    @staticmethod
    def get_weighted_recommendation(recommendations):
        weights = len(recommendations) - np.arange(len(recommendations), dtype=np.float32)
        weights *= weights * weights * weights
        weights /= weights.sum()

        return int(np.random.choice(recommendations, p=weights))

    def recommend_next(self, user: int, prev_track: int, prev_track_time: float) -> int:
        recommendations = self.recommendations_redis.get(user)
        if recommendations is None:
            return self.fallback.recommend_next(user, prev_track, prev_track_time)

        recommendations = list(self.catalog.from_bytes(recommendations))
        if recommendations is None:
            return self.fallback.recommend_next(user, prev_track, prev_track_time)

        if prev_track not in recommendations:
            return RandomWalkIndexed.get_weighted_recommendation(recommendations)

        index = recommendations.index(prev_track)
        if index == 0 or index == len(recommendations) - 1:
            recommendations.pop(index)
            return RandomWalkIndexed.get_weighted_recommendation(recommendations)

        if np.random.random() < 0.1:
            return RandomWalkIndexed.get_weighted_recommendation(recommendations[:index])
        else:
            return RandomWalkIndexed.get_weighted_recommendation(recommendations[(index + 1):])
