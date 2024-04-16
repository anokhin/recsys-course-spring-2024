import random
from collections import Counter

from .recommender import Recommender


class Custom(Recommender):
    def __init__(
        self,
        recommendations_redis, 
        tracks_redis, 
        artists_redis,
        catalog,
        fallback: Recommender,
    ):
        self.recommendations_redis = recommendations_redis
        self.tracks_redis = tracks_redis
        self.artists_redis = artists_redis
        self.catalog = catalog
        self.fallback = fallback

        self._artist_counter = Counter()
        self._dssm_recommender = True

    def recommend_next(
        self,
        user: int,
        prev_track: int,
        prev_track_time: float,
    ) -> int:
        track_data = self.tracks_redis.get(prev_track)
        if track_data is not None:
            track = self.catalog.from_bytes(track_data)
        else:
            raise ValueError(f"Track not found: {prev_track}")

        self._artist_counter[track.artist] += 1

        if not self._dssm_recommender:
            return self._fallback_strategy(user, prev_track, prev_track_time)

        if prev_track_time < 0.1:
            self._dssm_recommender = False
            return self._fallback_strategy(user, prev_track, prev_track_time)

        user_recommendations = self.recommendations_redis.get(user)
        if user_recommendations is None:
            return self.fallback.recommend_next(user, prev_track, prev_track_time)

        user_recommendations = self.catalog.from_bytes(user_recommendations)
        index = (
            user_recommendations.index(prev_track) + 1 
            if prev_track in user_recommendations 
            else 0
        )
        return user_recommendations[index % len(user_recommendations)]

    def _fallback_strategy(
        self, 
        user: int,
        prev_track: int,
        prev_track_time: float,
    ):
        if random.random() < 0.3:
            return self._get_recommendation_by_artist()
        else:
            return self.fallback.recommend_next(user, prev_track, prev_track_time)

    def _get_recommendation_by_artist(self):
        most_interested_artist = self._artist_counter.most_common(1)[0][0]

        artist_data = self.artists_redis.get(most_interested_artist)
        if artist_data is not None:
            artist_tracks = self.catalog.from_bytes(artist_data)
        else:
            raise ValueError(f"Artist not found: {most_interested_artist}")

        return artist_tracks[random.randint(0, len(artist_tracks) - 1) % len(artist_tracks)]
