import random

from .recommender import Recommender


class SessionIndexedContextual(Recommender):
    def __init__(self, contextual_recommendations_redis, users_recommendations_redis,
                 catalog, fallback):
        self.contextual_recommendations_redis = contextual_recommendations_redis
        self.users_recommendations_redis = users_recommendations_redis
        self.fallback = fallback
        self.catalog = catalog

    def recommend_next(self, user: int, prev_track: int, prev_track_time: float) -> int:
        first_track = self.catalog.first_tracks[user]
        recommendations = self.users_recommendations_redis.get(user)
        if recommendations is None:
            return self.fallback.recommend_next(user, prev_track, prev_track_time)

        previous_track_recs = self.contextual_recommendations_redis.get(prev_track)
        if previous_track_recs is not None:
            previous_track_recs = set(self.catalog.from_bytes(previous_track_recs))
        else:
            previous_track_recs = []

        sessions = self.catalog.from_bytes(recommendations)
        sessions = [set(v) for v in sessions]
        best_session = sessions[0]
        best_score = 0
        for session in sessions:
            score = 0
            if first_track in session:
                score += 2
            if prev_track in session:
                score += prev_track_time - 0.5
            if score > best_score:
                best_score = score
                best_session = session
        best_session = list(best_session)
        for recommendation in best_session:
            if recommendation in self.catalog.sessions[user]:
                continue
            if recommendation in previous_track_recs:
                return recommendation
            if random.random() > 0.9:
                return recommendation
        return best_session[0]
