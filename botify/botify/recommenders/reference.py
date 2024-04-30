import random
import typing as tp
from dataclasses import dataclass

from .recommender import Recommender


@dataclass
class RelevantTrack:
    user: int
    track: int
    time: float


class Reference(Recommender):
    def __init__(self, recommendations_dssm, recommendations_contextual, catalog, fallback) -> None:
        self.recommendations_dssm = recommendations_dssm
        self.recommendations_contextual = recommendations_contextual
        self.fallback = fallback
        self.catalog = catalog
        self.dssm_idx: int = 0
        self.irrelevant_count: int = 0
        self.upper_threshold: float = 0.5
        self.lower_threshold: float = 0.12
        self.listened_tracks: tp.List[int] = []
        self.relevant_tracks: tp.List[int] = []
        self.most_relevant_track: tp.Optional[RelevantTrack] = None

    def recommend_next(self, user: int, prev_track: int, prev_track_time: float) -> int:
        self.maintain_features(prev_track, prev_track_time)
        self.store_most_relevant(user, prev_track, prev_track_time)

        # If dssm gives bad tracks condition was true, then try to recommend with custom contextual recommender
        if self.irrelevant_count >= 3:
            next_track = self.custom_contextual(user, prev_track, prev_track_time)
            return self.check_listened(next_track, user, prev_track, prev_track_time)

        # Greedy dssm recommender
        recommendations = self.recommendations_dssm.get(user)
        if recommendations is not None:
            recommendations_lst = list(self.catalog.from_bytes(recommendations))
            self.dssm_idx = self.update_dssm_idx(prev_track, recommendations_lst)
            next_track = recommendations_lst[self.dssm_idx]
            return self.check_listened(next_track, user, prev_track, prev_track_time)
        else:
            next_track = self.fallback.recommend_next(user, prev_track, prev_track_time)
            return next_track

    def maintain_features(self, prev_track: int, prev_track_time: float) -> None:
        self.listened_tracks.append(prev_track)
        if prev_track_time < self.lower_threshold:
            self.irrelevant_count += 1
        elif prev_track_time > self.upper_threshold:
            self.relevant_tracks.append(prev_track)
            self.irrelevant_count: int = 0
        else:
            self.irrelevant_count: int = 0

    def store_most_relevant(self, user: int, prev_track: int, prev_track_time: float) -> None:
        if self.dssm_idx == 0:
            self.most_relevant_track = RelevantTrack(user, prev_track, prev_track_time)
        if prev_track_time > self.most_relevant_track.time:
            self.most_relevant_track = RelevantTrack(user, prev_track, prev_track_time)

    @staticmethod
    def update_dssm_idx(prev_track: int, recommendations: tp.List[int]) -> int:
        return (recommendations.index(prev_track) + 1) % len(recommendations) if prev_track in recommendations else 0

    def custom_contextual(self, user: int, prev_track: int, prev_track_time: float) -> int:
        if self.most_relevant_track is not None:
            next_track = self.contextual_recommend_next(
                user,
                prev_track,
                prev_track_time,
                self.most_relevant_track.track
            )
            return next_track
        if self.relevant_tracks:
            some_relevant = self.get_random_relevant()
            next_track = self.contextual_recommend_next(
                user,
                prev_track,
                prev_track_time,
                some_relevant
            )
            return next_track
        else:
            next_track = self.fallback.recommend_next(user, prev_track, prev_track_time)
            return next_track

    def contextual_recommend_next(self, user: int, prev_track: int, prev_track_time: float, some_relevant_track) -> int:
        # 1. Fall back to Random if there is no one relevant track
        similar_tracks = self.recommendations_contextual.get(some_relevant_track)
        next_track = self.fallback.recommend_next(user, prev_track, prev_track_time)
        if similar_tracks is None:
            return next_track

        # 2. Get recommendations for similar tracks, fall back to Random if there is no recommendations
        similar_tracks_lst: tp.List[int] = list(self.catalog.from_bytes(similar_tracks))
        if not similar_tracks_lst:
            return next_track

        # 3. Get random track from the recommendation list
        next_track: int = self.get_random_next(similar_tracks_lst)
        return next_track

    def check_listened(self, track_to_check, user: int, prev_track: int, prev_track_time: float, ) -> int:
        if track_to_check in self.listened_tracks:
            return self.fallback.recommend_next(user, prev_track, prev_track_time)
        else:
            return track_to_check

    def get_random_relevant(self) -> int:
        some_relevant_track: int = random.choice(self.relevant_tracks)
        self.relevant_tracks.remove(some_relevant_track)
        return some_relevant_track

    @staticmethod
    def get_random_next(similar_tracks_lst: tp.List[int]) -> int:
        shuffled = similar_tracks_lst
        random.shuffle(shuffled)
        next_track = shuffled[0]
        return next_track
