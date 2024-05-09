from .random import Random
from .recommender import Recommender
import random

TRACK_DURATION = 0.5

class ContextualMod(Recommender):
    def __init__(self, tracks_redis, catalog, fallback, recommendations_redis):
        self.tracks_redis = tracks_redis
        self.recommendations_redis = recommendations_redis
        self.fallback = fallback
        self.catalog = catalog

    def recommend_next(self, user: int, prev_track: int, prev_track_time: float) -> int:

        if prev_track_time < TRACK_DURATION:
            recommendations = self.recommendations_redis.get(user)
            if recommendations is not None:
                shuffled = list(self.catalog.from_bytes(recommendations))
                random.shuffle(shuffled)
                return shuffled[0]
            else:
                return self.fallback.recommend_next(user, prev_track, prev_track_time)

        previous_track = self.tracks_redis.get(prev_track)
        recommendations = self.catalog.from_bytes(previous_track)
        if not recommendations:
            recommendations = self.recommendations_redis.get(user)
            if recommendations is not None:
                shuffled = list(self.catalog.from_bytes(recommendations))
                random.shuffle(shuffled)
                return shuffled[0]
            else:
                return self.fallback.recommend_next(user, prev_track, prev_track_time)

        shuffled = list(recommendations)
        random.shuffle(shuffled)
        return shuffled[0]
