import random
from .recommender import Recommender

class MyRecommender(Recommender):
    def __init__(self, tracks_redis, recommendations_redis, catalog, fallback, limit=0.65):
        self.tracks_redis = tracks_redis
        self.recommendations_redis = recommendations_redis
        self.fallback = fallback
        self.catalog = catalog
        self.limit = limit
        
    def recommend_next(self, user: int, last_track: int, last_track_time: float) -> int:
        recommendation_methods = [
            lambda: self._recommend_based_on_last_track(last_track, last_track_time),
            lambda: self._recommend_users_next(user)
        ]
    
        for method in recommendation_methods:
            result = method()
            if result is not None:
                return result
        
        return self.fallback.recommend_next(user, last_track, last_track_time)


    def _recommend_based_on_last_track(self, last_track, last_track_time):
        last_track = self.tracks_redis.get(last_track)
        if last_track is None or last_track_time < self.limit:
            return None

        recommendations = self.catalog.from_bytes(last_track)
        if recommendations:
            return self._pick_random(recommendations)
        
        return None

    def _recommend_users_next(self, user):
        recommendations = self.recommendations_redis.get(user)
        if recommendations:
            return self._pick_random(self.catalog.from_bytes(recommendations))
        
        return None

    def _pick_random(self, recommendations):
        return random.choice(recommendations) if recommendations else None
