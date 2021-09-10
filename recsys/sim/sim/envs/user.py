import json

import numpy as np
import scipy.special as ss

from .config import UserCatalogConfig
from .session import Session, Playback
from .track import TrackCatalog


class User:
    def __init__(
        self,
        user,
        interests,
        interest_neighbours,
        consume_bias,
        consume_sharpness,
        session_budget,
    ):
        self.user = user
        self.interests = interests
        self.interest_neighbours = interest_neighbours
        self.consume_bias = consume_bias
        self.consume_sharpness = consume_sharpness
        self.session_budget = session_budget

    def new_session(self, track_catalog: TrackCatalog):
        session_interest = np.random.choice(self.interests)
        session_interest_embedding = track_catalog.get_embedding(session_interest)

        nearest_tracks = track_catalog.get_nearest(
            session_interest_embedding, self.interest_neighbours
        )

        first_track = np.random.choice(
            [track for track in nearest_tracks[0] if track >= 0]
        )

        return Session(
            self.user, session_interest_embedding, first_track, self.session_budget
        )

    def consume(
        self, recommendation: int, session: Session, track_catalog: TrackCatalog
    ):
        time = self.listen(recommendation, session, track_catalog)
        budget_decrement = 1 if np.random.random() > time else 0

        session.update(Playback(recommendation, time), budget_decrement)

        if session.budget <= 0:
            session.finish()

        return time

    def listen(
        self, recommendation: int, session: Session, track_catalog: TrackCatalog
    ) -> float:
        # Users don't want to listen to the same track twice
        if recommendation in session:
            return 0.0

        recommendation_embedding = track_catalog.get_embedding(recommendation)
        score = np.dot(recommendation_embedding, session.embedding)
        return ss.expit((score - self.consume_bias) * self.consume_sharpness)

    def __repr__(self):
        return f"{self.user}"


class UserCatalog:
    def __init__(self, config: UserCatalogConfig):
        self.config = config
        self.users = []
        with open(config.user_catalog_path) as users_file:
            for line in users_file:
                user_data = json.loads(line)
                self.users.append(
                    User(
                        user_data["user"],
                        user_data["interests"],
                        user_data.get(
                            "interest_neighbours", config.default_interest_neighbours
                        ),
                        user_data.get("consume_bias", config.default_consume_bias),
                        user_data.get(
                            "consume_sharpness", config.default_consume_sharpness
                        ),
                        user_data.get("session_budget", config.default_session_budget),
                    )
                )

    def sample_user(self):
        return np.random.choice(self.users)

    def size(self):
        return len(self.users)
