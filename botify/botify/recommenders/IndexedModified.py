import random
from .recommender import Recommender


class IndexedModified(Recommender):
    def __init__(self, recommendations_redis, recommendations_div, catalog, fallback):
        self.recommendations_redis = recommendations_redis
        self.recommendations_div = recommendations_div
        self.fallback = fallback
        self.catalog = catalog
        self.user_track_history = {}

    def recommend_next(self, user: int, prev_track: int, prev_track_time: float) -> int:
        recommendations = self.recommendations_redis.get(user)

        previous_track = self.recommendations_div.get(prev_track)
        recommendations_div = None

        if previous_track is not None:
            # 2. Get recommendations for previous track, fall back to Random if there is no recommendations
            recommendations_div = self.catalog.from_bytes(previous_track)

        print(recommendations)
        print(recommendations_div)

        if recommendations is not None:

            recommendations_list = list(
                self.catalog.from_bytes(recommendations))

            if user in self.user_track_history:
                recommendations_list = [
                    track for track in recommendations_list if track not in self.user_track_history[user]]

            if recommendations_div:
                recommendations_div_set = set(
                    self.catalog.from_bytes(recommendations))
                common = recommendations_div_set.intersection(
                    set(recommendations_list))

                if common:
                    recommendations_list = list(common)

            random.shuffle(recommendations_list)
            next_recommendation = recommendations_list[0] if recommendations_list else None

            if user not in self.user_track_history:
                self.user_track_history[user] = set()
            if next_recommendation is not None:
                self.user_track_history[user].add(next_recommendation)
                return next_recommendation

        return self.fallback.recommend_next(user, prev_track, prev_track_time)
