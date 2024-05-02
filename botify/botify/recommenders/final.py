import pickle
from collections import defaultdict

from .recommender import Recommender


class Final(Recommender):
    def __init__(self, recommendations_redis, sessions_redis, tracks_redis, catalog, fallback):
        self.recommendations_redis = recommendations_redis
        self.sessions_redis = sessions_redis
        self.tracks_redis = tracks_redis
        self.catalog = catalog
        self.fallback = fallback

    def recommend_next(self, user: int, session_id: int, prev_track: int, prev_track_time: float) -> int:
        track_to_artist = dict()

        def get_artist(track: int) -> str:
            if track in track_to_artist:
                return track_to_artist[track]
            artist = pickle.loads(self.tracks_redis.get(track)).artist
            track_to_artist[track] = artist
            return artist

        recommendations = self.catalog.from_bytes(self.recommendations_redis.get(user))

        user_session = self.sessions_redis.get(session_id)
        user_session = pickle.loads(user_session) if user_session is not None else []
        user_session.append((prev_track, prev_track_time))
        self.sessions_redis.set(session_id, pickle.dumps(user_session))

        listened_tracks = {track for track, _ in user_session}

        artist_counts = defaultdict(int)
        for track, _ in user_session:
            artist_counts[get_artist(track)] += 1

        # filter out already listened tracks
        recommendations = [
            recommendation
            for recommendation in recommendations
            if recommendation not in listened_tracks
        ]
        # sort by artist counts ( stable -> Bubble sort <3 )
        n = len(recommendations)
        if n == 0:
            return self.fallback.recommend_next(user, session_id, prev_track, prev_track_time)

        for i in range(n - 1):
            swapped = False
            for j in range(n - i - 1):
                if artist_counts[get_artist(recommendations[j])] > artist_counts[get_artist(recommendations[j + 1])]:
                    recommendations[j], recommendations[j + 1] = recommendations[j + 1], recommendations[j]
                    swapped = True
            if not swapped:
                break

        recommended_track = recommendations[0]
        return recommended_track
