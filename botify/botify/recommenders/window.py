import random

from .recommender import Recommender


class Window(Recommender):
    def __init__(self, recommendations_redis, catalog, fallback,
                 sessions,
                 window_size: int = 2, 
        ):
        self.recommendations_redis = recommendations_redis
        self.fallback = fallback
        self.catalog = catalog
        self.sessions = sessions
        self.window_size = window_size 

    def recommend_next(self, user: int, prev_track: int, prev_track_time: float) -> int:
        if user not in self.sessions:
            self.sessions[user] = []
        session = self.sessions[user]
        session.append((prev_track, prev_track_time))
        
        recommendations = self.recommendations_redis.get(user)
        if recommendations is None:
            return self.fallback.recommend_next(user, prev_track, prev_track_time)
        recommendations = list(self.catalog.from_bytes(recommendations))
                            
        if prev_track not in recommendations:
            return random.choice(recommendations)
        
        len_rec = len(recommendations)
        
        rec_prev_track_ind = recommendations.index(prev_track)
        l = (rec_prev_track_ind - self.window_size + 3 * len_rec) % len_rec
        r = (rec_prev_track_ind + self.window_size + 3 * len_rec + 1) % len_rec
        
        if l < r:
            inner_candidates = recommendations[l:rec_prev_track_ind] + recommendations[rec_prev_track_ind + 1: r]
            outher_candidates = recommendations[:l] + recommendations[r + 1:]
            
        else:
            outher_candidates = recommendations[l:rec_prev_track_ind] + recommendations[rec_prev_track_ind + 1: r]
            inner_candidates = recommendations[:l] + recommendations[r + 1:]
        
        inner_candidates = list(set(inner_candidates) - \
            set([track for track, track_time in session]))
        
        outher_candidates = list(set(outher_candidates) - \
            set([track for track, track_time in session]))
        
        if not inner_candidates:
            inner_track = recommendations[
                (rec_prev_track_ind + self.window_size) % len(recommendations)
            ]
        else:
            inner_track = random.choice(inner_candidates)
        
        if not outher_candidates:
            outher_track = recommendations[
                (rec_prev_track_ind + self.window_size) % len(recommendations)
            ]
        else:
            outher_track = random.choice(outher_candidates)
        
        if prev_track_time > 0.6:
            return inner_track
        else:
            return outher_track



