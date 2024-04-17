import random
import numpy as np
import scipy.stats as ss

from .recommender import Recommender


class BetterIndexed(Recommender):
    def __init__(self, recommendations_redis, tracks_redis, artists_redis, catalog, fallback):
        self.recommendations_redis = recommendations_redis
        self.tracks_redis = tracks_redis
        self.artists_redis = artists_redis
        self.fallback = fallback
        self.catalog = catalog
        self.last10 = dict()

    def recommend_next(self, user: int, prev_track: int, prev_track_time: float) -> int:
        recommendations = self.recommendations_redis.get(user)

        if user in self.last10:
            self.last10[user] = self.last10[user] + [prev_track]
            if len(self.last10[user] > 10):
                self.last10[user].pop()
        else:
            self.last10[user] = [prev_track]

        if recommendations is not None:
                shuffled = list(self.catalog.from_bytes(recommendations))
                random.shuffle(shuffled)

                if prev_track_time > 0.8:
                    i = 0
                    while i < len(shuffled) - 1:
                        track_data = self.tracks_redis.get(prev_track)
                        if track_data is not None:
                            track = self.catalog.from_bytes(track_data)
                        else:
                            raise ValueError(f"Track not found: {prev_track}")
                        
                        track_data2 = self.tracks_redis.get(shuffled[i])
                        if track_data2 is not None:
                            track2 = self.catalog.from_bytes(track_data2)
                        else:
                            raise ValueError(f"Track not found")
                        if track.artist == track2.artist and prev_track != shuffled[i]:
                            flag = True
                            for lasttrack in self.last10[user]:
                                if shuffled[i] == lasttrack:
                                    flag = False
                                    break
                            if flag:
                                return shuffled[i]
                        i += 1


                
                if prev_track_time < 0.05:
                    i = 0
                    while i < len(shuffled) - 1:
                        track_data = self.tracks_redis.get(prev_track)
                        if track_data is not None:
                            track = self.catalog.from_bytes(track_data)
                        else:
                            raise ValueError(f"Track not found: {prev_track}")
                        
                        track_data2 = self.tracks_redis.get(shuffled[i])
                        if track_data2 is not None:
                            track2 = self.catalog.from_bytes(track_data2)
                        else:
                            raise ValueError(f"Track not found")
                        if track.artist != track2.artist:
                            flag = True
                            for lasttrack in self.last10[user]:
                                if shuffled[i] == lasttrack:
                                    flag = False
                                    break
                            if flag:
                                return shuffled[i]
                        i += 1
                
                i = 0
                while i < len(shuffled) - 1:
                    flag = True
                    for lasttrack in self.last10[user]:
                        if shuffled[i] == lasttrack:
                            flag = False
                            break
                    if flag:
                        return shuffled[i]
                    i += 1
                
        else:
            return self.fallback.recommend_next(user, prev_track, prev_track_time)