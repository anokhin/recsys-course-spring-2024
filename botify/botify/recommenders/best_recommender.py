import random

from .recommender import Recommender


class BestRecommender(Recommender):
    def __init__(self, recommendations_redis, artist_memory_redis, track_memory_redis, tracks_redis, catalog, fallback):
        self.recommendations_redis = recommendations_redis
        self.tracks_redis = tracks_redis
        self.artist_memory = artist_memory_redis
        self.track_memory = track_memory_redis
        self.fallback = fallback
        self.catalog = catalog

    def recommend_next(self, user: int, prev_track: int, prev_track_time: float) -> int:
        recommendations = self.recommendations_redis.get(user)
        track_mem = self.track_memory.get(user)
        artist_mem = self.artist_memory.get(user)

        if track_mem is not None:
            track_mem = list(self.catalog.from_bytes(track_mem))
        else:
            track_mem = []

        if artist_mem is not None:
            artist_mem = list(self.catalog.from_bytes(artist_mem))
        else:
            artist_mem = []

        repeats = 0
        if recommendations is not None:
            recs = list(self.catalog.from_bytes(recommendations))
            while True:
                repeats += 1
                if repeats == 10:
                    return self.fallback.recommend_next(user, prev_track, prev_track_time)
                random.shuffle(recs)
                track_num = recs[0]
                track_data = self.tracks_redis.get(track_num)
                track = self.catalog.from_bytes(track_data)

                if track_num in track_mem:
                    continue

                track_mem.append(track_num)
                self.track_memory.set(user, self.catalog.to_bytes(track_mem))

                artists = sum(1 for i in artist_mem if i == track.artist)
                if artists < 3:
                    artist_mem.append(track.artist)
                    track_mem.append(track_num)
                    self.track_memory.set(user, self.catalog.to_bytes(track_mem))
                    self.artist_memory.set(user, self.catalog.to_bytes(artist_mem))
                    return track_num
        else:
            return self.fallback.recommend_next(user, prev_track, prev_track_time)
