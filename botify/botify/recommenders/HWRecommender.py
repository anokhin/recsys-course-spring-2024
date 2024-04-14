from .recommender import Recommender


class HWRecommender(Recommender):
    def __init__(self, recommendations_redis, catalog, fallback):
        self.recommendations_redis = recommendations_redis
        self.fallback = fallback
        self.catalog = catalog

    def recommend_next(self, user: int, prev_track: int, prev_track_time: float) -> int:
        recommendations = self.recommendations_redis.get(user)

        if recommendations is None:
            return self.fallback.recommend_next(user, prev_track, prev_track_time)

        recommendations = list(self.catalog.from_bytes(recommendations))

        if prev_track not in recommendations:
            return recommendations[0]

        i = recommendations.index(prev_track)

        if prev_track_time < 0.3 and i > 5:
            return recommendations[0]

        return recommendations[(i + 1) % len(recommendations)]
