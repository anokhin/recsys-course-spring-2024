import pickle
import random

from .recommender import Recommender


class IndexedNew(Recommender):
    def __init__(
        self,
        recommendations_redis,
        *,
        fallback: Recommender,
    ):
        self._recommendations_redis = recommendations_redis
        self._fallback = fallback

    def recommend_next(
        self,
        user: int,
        prev_track: int,
        prev_track_time: float,
    ) -> int:
        def fallback():
            return self._fallback.recommend_next(
                user, prev_track, prev_track_time)
        raw_recommendations = self._recommendations_redis.get(user)
        if raw_recommendations is None:
            return fallback()
        recommendations = pickle.loads(raw_recommendations)
        if prev_track not in recommendations:
            return recommendations[0]
        index = recommendations.index(prev_track)
        return recommendations[(index + 1) % len(recommendations)]
