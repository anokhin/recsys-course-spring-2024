from .random import Random
from .recommender import Recommender
import random

SOLUTION_TIME = 0.65 #2.18314

class ContextualMod(Recommender):
    def __init__(self, tracks_redis, catalog, fallback, recommendations_redis):
        self.tracks_redis = tracks_redis
        self.recommendations_redis = recommendations_redis
        self.fallback = fallback
        self.catalog = catalog
        self.users_preferences = {}

    def recommend_next(self, user: int, prev_track: int, prev_track_time: float) -> int:
        if user not in self.users_preferences:
            self.users_preferences[user] = []

        previous_track = self.tracks_redis.get(prev_track)
        if previous_track is None:
            return self.fallback.recommend_next(user, prev_track, prev_track_time)

        if prev_track_time < SOLUTION_TIME:
            recommendations = self.recommendations_redis.get(user)
            if recommendations is not None:
                shuffled = list(self.catalog.from_bytes(recommendations))
                random.shuffle(shuffled)
                return shuffled[0]
            else:
                return self.fallback.recommend_next(user, prev_track, prev_track_time)

        recommendations = self.catalog.from_bytes(previous_track)
        if not recommendations:
            return self.fallback.recommend_next(user, prev_track, prev_track_time)

        shuffled = list(recommendations)
        random.shuffle(shuffled)
        return shuffled[0]
