import random
import scipy.stats
import numpy as np
from .recommender import Recommender


class BestIndexed(Recommender):
    def __init__(self, recommendations_redis, catalog, fallback, recomendations_lfm):
        self.recommendations_redis = recommendations_redis
        self.fallback = fallback
        self.catalog = catalog
        self.recommendations_lfm = recomendations_lfm

    def recommend_next(self, user: int, prev_track: int, prev_track_time: float) -> int:
        recommendations_dssm = self.recommendations_redis.get(user)

        
        if recommendations_dssm is not None: 
            # NOTE: Воспользуемся рекомендерем lightFM в случае, если рекомендации dssm пользователю не понравились
            if prev_track_time < 0.3:
                recommendations_lfm = self.recommendations_lfm.get(user)
                if recommendations_lfm:
                    recs_lfm = list(self.catalog.from_bytes(recommendations_lfm))
                    random.shuffle(recs_lfm)
                    return recs_lfm[0]
                
            # NOTE: В противном случае пользуемся dssm, но если предыдущий трек, прослушанный пользователем, есть в 
            # списке рекомендаций, можно вернуть следующий за ним. То есть отдает треки в порядке "близости" по мнению
            # DSSM 
            recs_dssm = list(self.catalog.from_bytes(recommendations_dssm))

            if len(recs_dssm) != 0:
                if prev_track not in recs_dssm:
                    return recs_dssm[0]
                else:
                    for i in range(1, len(recs_dssm)):
                        if recs_dssm[i-1] == prev_track:
                            rec = recs_dssm[i]
                            return rec
                        
            # NOTE: В самом плохом случае возвращаем просто людой из треков, предсказанных DSSM            
            random.shuffle(recs_dssm)
            return recs_dssm[0]
        else:
            # NOTE: Иначе падаем в рандомный рекомендер
            return self.fallback.recommend_next(user, prev_track, prev_track_time)
