from .random import Random
from .recommender import Recommender
import random


class Contextual(Recommender):
    """
    Recommend tracks closest to the previous one.
    Fall back to the random recommender if no
    recommendations found for the track.
    """
    def __init__(self, tracks_redis, catalog, fallback):
        self.tracks_redis = tracks_redis
        self.fallback = fallback
        self.catalog = catalog

    def recommend_next(self, user: int, session_id: int, prev_track: int, prev_track_time: float) -> int:
        # 1. Get previous track from redis DB, fall back to Random if there is no one

        previous_track = self.tracks_redis.get(prev_track)
        if previous_track is None:
            return self.fallback.recommend_next(user, session_id, prev_track, prev_track_time)

        # 2. Get recommendations for previous track, fall back to Random if there is no recommendations
        recommendations = self.catalog.from_bytes(previous_track)
        if not recommendations:
            return self.fallback.recommend_next(user, session_id, prev_track, prev_track_time)

        # 3. Get random track from the recommendation list
        shuffled = list(recommendations)
        random.shuffle(shuffled)
        return shuffled[0]
