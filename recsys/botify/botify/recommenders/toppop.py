import random
from typing import List

from .recommender import Recommender


class TopPop(Recommender):
    def __init__(self, top_tracks: List[int]):
        self.top_tracks = top_tracks

    def recommend_next(self, user: int, prev_track: int, prev_track_time: float) -> int:
        shuffled = list(self.top_tracks)
        random.shuffle(shuffled)
        return shuffled[0]
