import numpy

from .recommender import Recommender


class HW2Recommender(Recommender):
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
                prev_idx = recommendations.index(prev_track)
                next_idx = (prev_idx + 1) % len(recommendations)
                if prev_idx >= 10 and prev_track_time < 0.01:
                    next_idx = 0
                elif next_idx >= 10 and prev_track_time < 0.3:
                    next_idx = (prev_idx + numpy.random.geometric(p=0.5)) % len(recommendations)
                                                    
                return recommendations[next_idx]
        else:
            return self.fallback.recommend_next(user, prev_track, prev_track_time)