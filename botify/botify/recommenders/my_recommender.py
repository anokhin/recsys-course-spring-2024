from .recommender import Recommender
import random


class MyRecommender(Recommender):
    def __init__(self, recommendations_dssm_redis, recommendations_contextual_redis, top_tracks, catalog, fallback):
        self.recommendations_dssm_redis = recommendations_dssm_redis
        self.recommendations_contextual_redis = recommendations_contextual_redis
        self.top_tracks = top_tracks
        self.catalog = catalog
        self.fallback = fallback

    def _get_track_info(self, track_id: int):
        return next((track for track in self.catalog.tracks if track.track == track_id), None)

    def _get_dssm_recommendations(self, user: int):
        recommendations_bytes = self.recommendations_dssm_redis.get(user)
        if recommendations_bytes:
            recommendations = self.catalog.from_bytes(recommendations_bytes)
            return list(recommendations)
        return None

    def _get_contextual_recommendations(self, prev_track: int):
        track_info = self._get_track_info(prev_track)
        if track_info:
            return track_info.recommendations
        return None

    def recommend_next(self, user: int, prev_track: int, prev_track_time: float) -> int:
        dssm_recommendations = self._get_dssm_recommendations(user)
        if dssm_recommendations:
            total_popularity = sum(self._get_track_info(track_id).pop for track_id in dssm_recommendations)
            weighted_choices = [(track_id, self._get_track_info(track_id).pop / total_popularity) for track_id in dssm_recommendations]
            chosen_track = random.choices([track for track, weight in weighted_choices], [weight for track, weight in weighted_choices], k=1)[0]
            return chosen_track

        contextual_recommendations = self._get_contextual_recommendations(prev_track)
        if contextual_recommendations:
            return max(contextual_recommendations, key=lambda track_id: self._get_track_info(track_id).pop)

        if self.top_tracks:
            return random.choice(self.top_tracks)

        return self.fallback.recommend_next(user, prev_track, prev_track_time)
