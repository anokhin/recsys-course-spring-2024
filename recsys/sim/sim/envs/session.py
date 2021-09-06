from dataclasses import dataclass


@dataclass
class Playback:
    song: int
    time: float


class Session:
    def __init__(self, user: int, first_song: int):
        self.user = user
        self.finished = False
        self.playback = [Playback(first_song, 1.0)]

    def observe(self):
        observation = {"user": self.user}

        # Observe initial song only upon the session start
        if len(self.playback) == 1:
            observation["song"] = self.playback[0].song

        return observation

    def update(self, playback: Playback):
        self.playback.append(playback)

    def finish(self):
        self.finished = True

    def __repr__(self):
        return f"{self.user}:{self.playback}" + "." if self.finished else ""
