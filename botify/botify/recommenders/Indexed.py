import random

from .recommender import Recommender


class Indexed(Recommender):
    def __init__(self, recommendations_redis, catalog, fallback):
        self.recommendations_redis = recommendations_redis
        self.fallback = fallback
        self.catalog = catalog

    def recommend_next(self, user: int, prev_track: int, prev_track_time: float) -> int:
        recommendations = self.recommendations_redis.get(user)

        if recommendations is not None:
            shuffled = list(self.catalog.from_bytes(recommendations))
            random.shuffle(shuffled)
            return shuffled[0]
        else:
            return self.fallback.recommend_next(user, prev_track, prev_track_time)


class MyIndexed(Recommender):

    def __init__(self, recommendations_redis, catalog, fallback, weighted_recs):
        self.recommendations_redis = recommendations_redis
        self.fallback = fallback
        self.catalog = catalog
        self.weighted_recs = weighted_recs
        

    def recommend_next(self, user: int, prev_track: int, prev_track_time: float) -> int:
        weighted_recs = self.weighted_recs
        recommendations = self.recommendations_redis.get(user)
        if recommendations is  None:
            return self.fallback.recommend_next(user, prev_track, prev_track_time)

        recs = list(self.catalog.from_bytes(recommendations))

        if weighted_recs[user] is None:
            weighted_recs[user] = [[0, i, rec] for i, rec in enumerate(recs)]

        for rec in weighted_recs[user]: # эвристика для плохих треков
            if rec[2] == prev_track:
                rec[0] = 1
                rec[1] += (0.5 - prev_track_time) * 10

        weighted_recs[user] = sorted(weighted_recs[user])

        if weighted_recs[user][0][0] == 1:
            for rec in weighted_recs[user]:
                rec[0] = 0

        return weighted_recs[user][0][2]
