from .recommender import Recommender

import numpy
import random


class CustomRecommender(Recommender):
    def __init__(self, recommendations_redis, catalog, top_tracks, fallback):
        self.recommendations_redis = recommendations_redis
        self.fallback = fallback
        self.catalog = catalog
        self.top_tracks = top_tracks

    def recommend_next(self, user: int, prev_track: int, prev_track_time: float) -> int:
        recommendations = self.recommendations_redis.get(user)

        if recommendations is not None:
            list_recommendations = list(self.catalog.from_bytes(recommendations))

            if prev_track in self.top_tracks:
                liked_top = prev_track_time >= 0.8
                rec_top = []
                for track in self.top_tracks:
                    if track in list_recommendations:
                        rec_top.append(track)
                if len(rec_top) > 5 and liked_top:
                    return int(numpy.random.choice(rec_top, 1)[0])

            if prev_track in list_recommendations:
                next_id = (list_recommendations.index(prev_track) + 1) % len(list_recommendations)
                return list_recommendations[next_id]

            random.shuffle(list_recommendations)
            return list_recommendations[0]

        return self.fallback.recommend_next(user, prev_track, prev_track_time)
