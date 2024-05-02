import pickle
from collections import defaultdict

from .recommender import Recommender


class DifferentArtist(Recommender):
    def __init__(self, track_redis, sessions_redis):
        self.track_redis = track_redis
        self.sessions_redis = sessions_redis

    def recommend_next(self, user: int, session_id: int, prev_track: int, prev_track_time: float) -> int:
        def get_artist(track: int) -> str:
            return pickle.loads(self.track_redis.get(track)).artist

        user_session = self.sessions_redis.get(user)
        user_session = pickle.loads(user_session) if user_session is not None else []
        user_session.append((prev_track, prev_track_time))
        self.sessions_redis.set(user, pickle.dumps(user_session))

        artist_counts = defaultdict(int)
        for track, _ in user_session:
            artist_counts[get_artist(track)] += 1

        while True:
            track = int(self.track_redis.randomkey())
            if artist_counts[get_artist(track)] == 0:
                break

        return track
