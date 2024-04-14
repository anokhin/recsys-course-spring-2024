import random

from .recommender import Recommender


class IndexedContextual(Recommender):
    def __init__(self, contextual_recommendations_redis, users_recommendations_redis,
                 catalog, fallback):
        self.contextual_recommendations_redis = contextual_recommendations_redis
        self.users_recommendations_redis = users_recommendations_redis
        self.fallback = fallback
        self.catalog = catalog

    def recommend_next(self, user: int, prev_track: int, prev_track_time: float) -> int:
        recommendations = self.users_recommendations_redis.get(user)

        if recommendations is not None:
            recommendations = self.catalog.from_bytes(recommendations)
            previous_track_recs = self.contextual_recommendations_redis.get(prev_track)
            if previous_track_recs is not None:
                previous_track_recs = set(self.catalog.from_bytes(previous_track_recs))
            else:
                previous_track_recs = []

            for recommendation in recommendations:
                if recommendation in self.catalog.sessions[user]:
                    continue
                if recommendation in previous_track_recs:
                    return recommendation
                if random.random() > 0.9:
                    return recommendation
            return recommendations[0]
        else:
            return self.fallback.recommend_next(user, prev_track, prev_track_time)
