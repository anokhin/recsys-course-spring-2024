import random

from .recommender import Recommender


class MyIndexed(Recommender):
    def __init__(self, recommendations_redis, catalog, fallback, used, best_track, tracks_redis):
        self.recommendations_redis = recommendations_redis
        self.fallback = fallback
        self.catalog = catalog
        self.used = used
        self.best_track = best_track
        self.tracks_redis = tracks_redis

    def recommend_next(self, user: int, prev_track: int, prev_track_time: float) -> int:
        recommendations = self.recommendations_redis.get(user)
        used = self.used.get(user)

        if used is not None:
            used = list(self.catalog.from_bytes(used))
        else:
            used = []

        if recommendations is not None:
            shuffled = list(self.catalog.from_bytes(recommendations))
            cnt = len(used)
            best_track = self.best_track.get(user)

            if best_track is not None:
                best_track = list(self.catalog.from_bytes(best_track))
            else:
                best_track = []
            previous_track = self.tracks_redis.get(prev_track)

            if previous_track is None:
                return self.fallback.recommend_next(user, prev_track, prev_track_time)

            if prev_track_time == 1.0:
                best_track.append(previous_track)
                self.best_track.set(user, self.catalog.to_bytes(best_track))

            if cnt >= len(shuffled):
                if len(best_track) == 0:
                    return self.fallback.recommend_next(user, prev_track, prev_track_time)

                random.shuffle(best_track)

                new_recommendations = self.catalog.from_bytes(best_track[0])

                if len(new_recommendations) == 0 or new_recommendations is None:
                    return self.fallback.recommend_next(user, prev_track, prev_track_time)

                return new_recommendations[random.randint(0, len(new_recommendations) - 1)]

            used.append(shuffled[cnt])
            self.used.set(user, self.catalog.to_bytes(used))
            return shuffled[cnt]
        else:
            return self.fallback.recommend_next(user, prev_track, prev_track_time)
