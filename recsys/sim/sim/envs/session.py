from dataclasses import dataclass


@dataclass
class Playback:
    track: int
    time: float


class Session:
    def __init__(self, user: int, first_track: int):
        self.user = user
        self.finished = False
        self.playback = [Playback(first_track, 0.0)]

    def observe(self):
        return {"user": self.user, "track": self.playback[-1].track}

    def update(self, playback: Playback):
        self.playback.append(playback)

    def finish(self):
        self.finished = True

    def __repr__(self):
        return f"{self.user}:{self.playback}" + "." if self.finished else ""
