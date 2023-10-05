from .recommender import Recommender


class Indexed(Recommender):
    def __init__(self, recommendations_redis, catalog, fallback):
        self.recommendations_redis = recommendations_redis
        self.fallback = fallback
        self.catalog = catalog

    def recommend_next(self, user: int, prev_track: int, prev_track_time: float) -> int:
        # TODO 2.2: Load recommendations from Redis and pick random one from the loaded list
        # TODO 2.3: Fall back if no recommendations found
        return self.fallback.recommend_next(user, prev_track, prev_track_time)
