import numpy as np

from .config import UserConfig
from .session import Session, Playback


class User:
    def __init__(self, config: UserConfig):
        self.config = config

    def new_session(self):
        return Session(
            self.config.user, np.random.randint(self.config.song_catalog_config.size)
        )

    def consume(self, recommendation: int, session: Session):
        time = np.random.random()

        session.update(Playback(recommendation, time))

        if np.random.random() < 0.1:
            session.finish()

        return time

    def __repr__(self):
        return f"{self.config.user}"
