import numpy as np

from .recommender import Recommender


def get_not_listened_before_track(list_recommendations: list, user_history: list) -> int:
    recommendation = list(np.setdiff1d(list_recommendations, user_history, assume_unique=True))
    return int(recommendation[0])


class Best(Recommender):

    def __init__(self, recommendations_redis, catalog, fallback):
        self.recommendations_redis = recommendations_redis
        self.catalog = catalog
        self.fallback = fallback
        self.database = dict()

    def __register_user(self, user: int) -> None:
        self.database[user] = set()

    def __remember_track_for_user(self, user: int, track: int) -> None:
        if user not in self.database.keys():
            self.__register_user(user)

        self.database[user].add(track)

    def recommend_next(self, user: int, prev_track: int, prev_track_time: float) -> int:
        self.__remember_track_for_user(user, prev_track)
        recommendations = self.recommendations_redis.get(user)

        if recommendations is not None:
            list_recommendations = list(self.catalog.from_bytes(recommendations))
            user_history = list(self.database[user])

            if prev_track not in list_recommendations:
                recommend_track = get_not_listened_before_track(list_recommendations, user_history)
            else:
                index = list_recommendations.index(prev_track)
                new_index = (index + 1) % len(list_recommendations)
                recommend_track = int(list_recommendations[new_index])

                if recommend_track in user_history:
                    recommend_track = get_not_listened_before_track(list_recommendations, user_history)
        else:
            recommend_track = self.fallback.recommend_next(user, prev_track, prev_track_time)

        self.__remember_track_for_user(user, recommend_track)
        return recommend_track
