import random

from .random import Random
from .recommender import Recommender


class StickyArtist(Recommender):
    def __init__(self, tracks_redis, artists_redis, catalog):
        self.fallback = Random(tracks_redis)
        self.tracks_redis = tracks_redis
        self.artists_redis = artists_redis
        self.catalog = catalog

    # TODO Seminar 1: step 3
    def recommend_next(self, user: int, prev_track: int, prev_track_time: float) -> int:
        return self.fallback.recommend_next(user, prev_track, prev_track_time)
