import random
from collections import defaultdict

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


class StrictIndexed(Recommender):
    def __init__(self, recommendations_redis, catalog, fallback):
        self.recommendations_redis = recommendations_redis
        self.fallback = fallback
        self.catalog = catalog
        self.liked_artists = defaultdict(set)
        self.last_tracks = defaultdict(list)
        self.disliked_tracks = defaultdict(set)

    def _update_last_tracks(self, user, track):
        if len(self.last_tracks[user]) < 60:
            self.last_tracks[user].append(track)
        else:
            self.last_tracks[user] = self.last_tracks[user][1:] + [track]

    def recommend_next(self, user: int, prev_track: int, prev_track_time: float) -> int:
        recommendations = self.recommendations_redis.get(user)

        if recommendations is not None:
            recs = list(self.catalog.from_bytes(recommendations))

            if prev_track_time > 0.8:
                self.disliked_tracks[user].discard(prev_track)

            if prev_track_time < 0.4:
                self.disliked_tracks[user].add(prev_track)

            for i, rec in enumerate(recs):
                if rec == prev_track:
                    first_disliked = None
                    for j in range(1, len(recs)):
                        next_track = recs[(i + j) % len(recs)]
                        if next_track not in self.last_tracks[user]:
                            if next_track not in self.disliked_tracks[user]:
                                self._update_last_tracks(user, next_track)
                                return next_track
                            elif first_disliked is None:
                                first_disliked = next_track
                    if first_disliked is not None:
                        self._update_last_tracks(user, first_disliked)
                        return first_disliked

            self._update_last_tracks(user, recs[0])
            return recs[0]
        else:
            return self.fallback.recommend_next(user, prev_track, prev_track_time)
