from dataclasses import dataclass
import numpy as np


@dataclass
class Playback:
    track: int
    time: float


class Session:
    def __init__(self, user: int, embedding: np.array, first_track: int, budget: int):
        self.user = user
        self.embedding = embedding
        self.budget = budget
        self.playback = [Playback(first_track, 0.0)]
        self.finished = False

    def observe(self):
        return {"user": self.user, "track": self.playback[-1].track}

    def update(self, playback: Playback, budget_decrement: int):
        self.playback.append(playback)
        self.budget -= budget_decrement

    def finish(self):
        self.finished = True

    def __contains__(self, track):
        return any([pb.track == track for pb in self.playback])

    def __repr__(self):
        return (
            f"{self.user}:{self.playback}:{self.budget}" + "." if self.finished else ""
        )
