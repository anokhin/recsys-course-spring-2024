from .recommender import Recommender
from .contextual import Contextual
from .Indexed import Indexed


class ContextualIndexed(Recommender):
    def __init__(self, tracks_redis, recommendations_redis, artists_redis, tracks_info_redis, catalog, fallback, thr=0.8, flg=False):
        self.tracks_redis = tracks_redis
        self.recommendations_redis = recommendations_redis
        self.fallback = fallback
        self.catalog = catalog
        self.thr = thr
        self.artists_redis = artists_redis
        self.flg = flg
        self.tracks_info_redis = tracks_info_redis

    def recommend_next(self, user: int, prev_track: int, prev_track_time: float) -> int:
        if prev_track_time > self.thr:
            recommender = Contextual(self.tracks_redis, self.catalog, self.fallback)
        else:
            recommender = Indexed(self.recommendations_redis, self.catalog, self.fallback)

        recommendation = recommender.recommend_next(user, prev_track, prev_track_time)

        track_data = self.tracks_info_redis.get(prev_track)
        if track_data is not None and self.flg:
            track = self.catalog.from_bytes(track_data)
            artist_data = self.artists_redis.get(track.artist)
            if artist_data is not None:
                artist_tracks = self.catalog.from_bytes(artist_data)
                if recommendation in artist_tracks:
                    recommendation = recommender.recommend_next(user, prev_track, prev_track_time)

        return recommendation
