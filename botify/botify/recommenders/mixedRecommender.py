from .random import Random
from .recommender import Recommender
import random
import numpy as np


class MixedRecommender(Recommender):
    def __init__(
            self,
            context_recommendations,
            recommendations_redis,
            catalog,
            fallback,
            divers_recs_path,
            patience=3,
            threshold_low=0.05,
            threshold_high=0.75
    ):
        self.context_recommendations = context_recommendations
        self.recommendations_redis = recommendations_redis
        self.fallback = fallback
        self.catalog = catalog
        self.threshold_low = threshold_low
        self.threshold_high = threshold_high
        self.patience = patience

        self.bad_recs = dict()
        # топ самых непохожих треков для каждого трека
        self.reversed_top_tracks = np.load(divers_recs_path)

    def clearBadRecommendations(self, user: int):
        self.bad_recs[user] = list()

    def addBadRecommendations(self, user: int, track: int):
        if user not in self.bad_recs:
            self.bad_recs[user] = list()
        self.bad_recs[user].append(track)

    def recommend_next(self, user: int, prev_track: int, prev_track_time: float) -> int:
        if prev_track_time >= self.threshold_low:
            self.clearBadRecommendations(user)

        # Если время прослушивания находится между границами, рекомендуем с помощью нейросетевого рекомендатора
        if prev_track_time >= self.threshold_low and prev_track_time <= self.threshold_high:
            return self.recommend_by_network(user, prev_track, prev_track_time)

        # Если время прослушивания меньше нижней границы
        if prev_track_time < self.threshold_low:
            self.addBadRecommendations(user, prev_track)
            if len(self.bad_recs[user]) >= self.patience:
                return self.recommend_opposite(user, prev_track, prev_track_time)
            # Если плохих рекомендаций было недостаточно много, продолжаем рекомендовать сетью
            return self.recommend_by_network(user, prev_track, prev_track_time)

        # Обрабатываем исключительные случаи
        prev_track_ctx_recommendation = self.context_recommendations.get(prev_track)
        if prev_track_ctx_recommendation is None:
            return self.fallback.recommend_next(user, prev_track, prev_track_time)
        recommendations = self.catalog.from_bytes(prev_track_ctx_recommendation)
        if not recommendations:
            return self.fallback.recommend_next(user, prev_track, prev_track_time)
        # Для времени прослушивания выше необходимиого порога рекомендуем наиболее похожий трек
        shuffled = list(recommendations)
        random.shuffle(shuffled)
        return shuffled[0]

    def recommend_opposite(self, user: int, prev_track: int, prev_track_time: float) -> int:
        opposite_tracks = set(self.reversed_top_tracks[self.bad_recs[user][0]])
        for i in range(1, len(self.bad_recs[user])):
            opposite_tracks = opposite_tracks & set(self.reversed_top_tracks[self.bad_recs[user][i]])
        if len(opposite_tracks) == 0:
            return self.fallback.recommend_next(user, prev_track, prev_track_time)
        rec_track = random.choice(list(opposite_tracks))
        return int(rec_track)
    def recommend_by_network(self, user: int, prev_track: int, prev_track_time: float) -> int:
        recommendations = self.recommendations_redis.get(user)

        if recommendations is not None:
            shuffled = list(self.catalog.from_bytes(recommendations))
            random.shuffle(shuffled)
            return shuffled[0]
        else:
            return self.fallback.recommend_next(user, prev_track, prev_track_time)