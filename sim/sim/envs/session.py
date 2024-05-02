from collections import Counter
from dataclasses import dataclass
from uuid import uuid4

import numpy as np


@dataclass
class Playback:
    track: int
    time: float
    artist: str = None


class Session:
    def __init__(
        self, user: int, embedding: np.array, first_playback: Playback, budget: int
    ):
        self.id = uuid4()
        self.user = user
        self.embedding = embedding
        self.budget = budget
        self.playback = [first_playback]
        self.finished = False

    def observe(self):
        return {"user": self.user, "track": self.playback[-1].track, "session_id": int(self.id)}

    def update(self, playback: Playback, budget_decrement: int):
        self.playback.append(playback)
        self.budget -= budget_decrement

    def finish(self):
        self.finished = True

    def artist_counts(self):
        return Counter([pb.artist for pb in self.playback])

    def __contains__(self, track):
        return any([pb.track == track for pb in self.playback])

    def __repr__(self):
        return (
            f"{self.user}:{self.playback}:{self.budget}" + "." if self.finished else ""
        )
