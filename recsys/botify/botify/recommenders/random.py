from .recommender import Recommender


class Random(Recommender):
    def __init__(self, redis):
        self.redis = redis

    def recommend_next(self, user: int) -> int:
        return int(self.redis.randomkey())
