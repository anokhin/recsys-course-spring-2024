from .random import Random
from .recommender import Recommender
import random


class ContextualWithIndexed(Recommender):
    """
    Recommend tracks closest to the previous one if user liked it.
    Else give him his personal recommendation.
    Fall back to the random recommender if no
    recommendations found for the track.
    """

    def __init__(self, tracks_redis, recommendations_redis, catalog, fallback, threshold=0.6):
        self.tracks_redis = tracks_redis
        self.recommendations_redis = recommendations_redis
        self.fallback = fallback
        self.catalog = catalog
        self.threshold = threshold
    def recommend_next(self, user: int, prev_track: int, prev_track_time: float) -> int:
        # 1. Get previous track from redis DB, fall back to Random if there is no one

        previous_track = self.tracks_redis.get(prev_track)
        if previous_track is None:
            return self.fallback.recommend_next(user, prev_track, prev_track_time)

        # 2. Check with user in mood for this type of items
        if prev_track_time < self.threshold:
            return self.recommend_users_next(user, prev_track, prev_track_time)


        # 3. Get recommendations for previous track, fall back to Random if there is no recommendations
        recommendations = self.catalog.from_bytes(previous_track)
        if not recommendations:
            return self.fallback.recommend_next(user, prev_track, prev_track_time)

        # 4. Get random track from the recommendation list
        shuffled = list(recommendations)
        random.shuffle(shuffled)
        return shuffled[0]

    def recommend_users_next(self, user: int, prev_track: int, prev_track_time: float) -> int:
        recommendations = self.recommendations_redis.get(user)

        if recommendations is not None:
            shuffled = list(self.catalog.from_bytes(recommendations))
            random.shuffle(shuffled)
            return shuffled[0]
        else:
            return self.fallback.recommend_next(user, prev_track, prev_track_time)