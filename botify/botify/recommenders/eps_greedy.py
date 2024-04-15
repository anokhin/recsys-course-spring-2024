import random
import queue

from .recommender import Recommender

class Epsilon_Greedy(Recommender):
    def __init__(self, recommendations_redis, catalog, fallback, epsilon=0.9):
        self.recommendations_redis = recommendations_redis
        self.fallback = fallback
        self.catalog = catalog
        self.user_likes = {}
        self.epsilons = {}
        self.epsilon = epsilon

    def recommend_next(self, user: int, prev_track: int, prev_track_time: float) -> int:
        recommendations = self.recommendations_redis.get(user)
        if user not in self.user_likes:
            self.user_likes[user] = queue.PriorityQueue()
            self.epsilons[user] = 1.0
        
        if random.random() < self.epsilons[user] or len(self.user_likes[user]) < 3:
            if recommendations is not None:
                recommendations = list(self.catalog.from_bytes(recommendations))
                if prev_track not in recommendations or prev_track_time < 0.3:
                    idx = random.randint(0, len(recommendations) - 1)
                else:
                    idx = (recommendations.index(prev_track) + 1) % len(recommendations)

                track = recommendations[idx]
            else:
                track = self.fallback.recommend_next(user, prev_track, prev_track_time)
            
            self.epsilons[user] *= self.epsilon
        else:
            _, track = self.user_likes[user].get()
    
        if prev_track_time > 0.85:
            self.user_likes[user].put((1.0 - prev_track_time, prev_track))
        return track
