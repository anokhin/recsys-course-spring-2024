import random

from .recommender import Recommender


class CustomRecommender(Recommender):
    def __init__(self, recommendations_redis, liked_tracks_redis, unliked_tracks_redis, catalog, callback, fallback):
        self.recommendations_redis = recommendations_redis
        self.liked_tracks_redis = liked_tracks_redis
        self.unliked_tracks_redis = unliked_tracks_redis
        self.callback = callback
        self.fallback = fallback
        self.catalog = catalog
        self.up_time_threshold = 0.85
        self.bottom_time_threshold = 0.35

    def __track_is_liked(self, prev_track_time: float) -> bool:
        return prev_track_time > self.up_time_threshold

    def __track_is_unliked(self, prev_track_time: float) -> bool:
        return prev_track_time < self.bottom_time_threshold

    def __get_liked_tracks(self, user: int) -> []:
        liked_tracks = []
        liked_tracks_bytes = self.liked_tracks_redis.get(user)
        if liked_tracks_bytes is not None:
            liked_tracks = list(self.catalog.from_bytes(liked_tracks_bytes))

        return liked_tracks

    def __get_unliked_tracks(self, user: int) -> []:
        unliked_tracks = []
        unliked_tracks_bytes = self.liked_tracks_redis.get(user)
        if unliked_tracks_bytes is not None:
            unliked_tracks = list(self.catalog.from_bytes(unliked_tracks_bytes))

        return unliked_tracks

    def recommend_next(self, user: int, prev_track: int, prev_track_time: float) -> int:
        recommendations_bytes = self.recommendations_redis.get(user)

        liked_tracks = self.__get_liked_tracks(user)
        unliked_tracks = self.__get_unliked_tracks(user)

        if self.__track_is_liked(prev_track):
            liked_tracks.append(prev_track)
            self.liked_tracks_redis.set(user, self.catalog.to_bytes(liked_tracks))

        if self.__track_is_unliked(prev_track):
            unliked_tracks.append(prev_track)
            self.unliked_tracks_redis.set(user, self.catalog.to_bytes(unliked_tracks))

        if recommendations_bytes is not None:
            recommendations = list(self.catalog.from_bytes(recommendations_bytes))
            if prev_track not in recommendations:
                return recommendations[0]
            index = recommendations.index(prev_track)
            dssm_recommendation = recommendations[(index + 1) % len(recommendations)]
            if index + 1 >= len(recommendations):
                if dssm_recommendation in liked_tracks:
                    return dssm_recommendation
                elif dssm_recommendation in unliked_tracks:
                    return random.choice(liked_tracks)
                else:
                    return self.callback.recommend_next(user, prev_track, prev_track_time)

            return recommendations[(index + 1) % len(recommendations)]
        else:
            return self.fallback.recommend_next(user, prev_track, prev_track_time)
