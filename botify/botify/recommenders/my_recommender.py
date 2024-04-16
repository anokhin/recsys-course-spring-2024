import random

from .recommender import Recommender


class MyRecommender(Recommender):
    def __init__(self, recommendations_dssm, catalog, fallback):
        self.recommendations_dssm = recommendations_dssm
        self.fallback = fallback
        self.catalog = catalog

    def recommend_next(self, user: int, prev_track: int, prev_track_time: float) -> int:
        recommendations = self.recommendations_dssm.get(user)

        if recommendations is not None:
            recommendations = list(self.catalog.from_bytes(recommendations))
            if prev_track not in recommendations:
                return recommendations[0]
            else:
                idx = (recommendations.index(prev_track) + 1) % len(recommendations)
                return recommendations[idx]
        else:
            return self.fallback.recommend_next(user, prev_track, prev_track_time)
