import pickle
import random

from .recommender import Recommender


class Custom(Recommender):
    def __init__(
        self,
        recommendations_dssm,
        recommendations_contextual,
        recommendations_lfm,
        catalog,
        fallback: Recommender,
    ):
        self._recommendations_dssm = recommendations_dssm
        self._fallback = fallback
        self.catalog = catalog
        self._recommendations_contextual = recommendations_contextual
        self._recommendations_lfm = recommendations_lfm

    def recommend_next(
        self,
        user: int,
        prev_track: int,
        prev_track_time: float,
    ) -> int:
        recommendations_from_dssm = self._recommendations_dssm.get(user)
        previous_track = self._recommendations_contextual.get(prev_track)
        recommendations_from_lfm = self._recommendations_lfm.get(user)

        if prev_track_time > 0.9 and previous_track is not None: # use contextual recommender

            recommendations = self.catalog.from_bytes(previous_track)
            if recommendations:
                shuffled = list(recommendations)
                random.shuffle(shuffled)
                return shuffled[0]
            
        if prev_track_time > 0.7 and recommendations_from_lfm is not None: # use lfm recommender
            recommendations = pickle.loads(recommendations_from_lfm)
            if prev_track in recommendations:
                index = recommendations.index(prev_track)
                offset = random.choice(range(1,4))
                rec_index = (index + offset) % len(recommendations)
                return recommendations[rec_index]

        #use dssm reccomender if all previous failed
        if recommendations_from_dssm is None:
            return self._fallback.recommend_next(
                user, prev_track, prev_track_time)
        recommendations = pickle.loads(recommendations_from_dssm)
        if prev_track not in recommendations:
            return random.choice(recommendations[:10])
        index = recommendations.index(prev_track)
        offset = random.choice(range(1,4))
        rec_index = (index + offset) % len(recommendations)
        return recommendations[rec_index]
