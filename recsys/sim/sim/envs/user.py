import numpy as np

from .config import UserCatalogConfig
from .session import Session, Playback
from .track import TrackCatalog


class User:
    def __init__(self, user):
        self.user = user

    def new_session(self, track_catalog: TrackCatalog):
        return Session(self.user, np.random.randint(track_catalog.size()))

    def consume(self, recommendation: int, session: Session):
        time = np.random.random()

        session.update(Playback(recommendation, time))

        if np.random.random() < 0.1:
            session.finish()

        return time

    def __repr__(self):
        return f"{self.user}"


class UserCatalog:
    def __init__(self, config: UserCatalogConfig):
        self.config = config
        self.users = [User(user) for user in range(config.users)]

    def sample_user(self):
        return np.random.choice(self.users)

    def size(self):
        return self.config.users
