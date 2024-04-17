from .recommender import Recommender


class MyIndexed(Recommender):
    def __init__(self, recommendations_redis, catalog, fallback):
        self.recommendations_redis = recommendations_redis
        self.fallback = fallback
        self.catalog = catalog
        self.start = [True] * 10000

    def recommend_next(self, user: int, prev_track: int, prev_track_time: float) -> int:
        recommendations = self.recommendations_redis.get(user)
        if recommendations is not None:
            lst = list(self.catalog.from_bytes(recommendations))
            if self.start[user] or prev_track not in lst:
                self.start[user] = False
                return lst[0]
            else:
                return lst[(lst.index(prev_track) + 1) % len(lst)]
        else:
            return self.fallback.recommend_next(user, prev_track, prev_track_time)
