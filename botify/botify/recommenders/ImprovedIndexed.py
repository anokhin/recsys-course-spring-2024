import random

from .recommender import Recommender


class ImprovedIndexed(Recommender):
    def __init__(self, recommendations_redis_dssm, recommendations_redis_lfm, catalog, fallback):
        self.recommendations_redis_dssm = recommendations_redis_dssm
        self.recommendations_redis_lfm = recommendations_redis_lfm
        self.fallback = fallback
        self.catalog = catalog

    def recommend_next(self, user: int, prev_track: int, prev_track_time: float) -> int:
        recommendations_dssm = self.recommendations_redis_dssm.get(user)
        recommendations_lfm = self.recommendations_redis_lfm.get(user)

        if recommendations_dssm is not None and recommendations_lfm is not None:

            if prev_track_time < 0.3:
                lfm_lst = list(self.catalog.from_bytes(recommendations_lfm))
                ind = random.randint(0, 4)
                return lfm_lst[-ind]

            else:
                dssm_lst = list(self.catalog.from_bytes(recommendations_dssm))
                played_index = dssm_lst.index(prev_track) if prev_track in dssm_lst else -1
                next_index = (played_index + 1) % len(dssm_lst)
                return dssm_lst[next_index]
        
        else:
            return self.fallback.recommend_next(user, prev_track, prev_track_time)
