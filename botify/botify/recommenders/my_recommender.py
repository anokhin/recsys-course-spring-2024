from .recommender import Recommender
import random


class MyRecommender(Recommender):
    def __init__(self, recommendations_dssm_redis, recommendations_contextual_redis, top_tracks, tracks_with_recs, catalog, fallback):
        self.recommendations_dssm_redis = recommendations_dssm_redis
        self.recommendations_contextual_redis = recommendations_contextual_redis
        self.top_tracks = top_tracks
        self.tracks_with_recs = tracks_with_recs
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
        contextual_recommendations = self._get_contextual_recommendations(prev_track)

        recs_by_tracks = None
        for track in self.tracks_with_recs:
            if track.track == prev_track:
                recs_by_tracks = track.recommendations
                break

        all_recommendations = set(dssm_recommendations if dssm_recommendations else [])
        if contextual_recommendations:
            all_recommendations.update(contextual_recommendations)
        if recs_by_tracks:
            all_recommendations.update(recs_by_tracks)

        all_recommendations_list = list(all_recommendations)

        if dssm_recommendations:
            weights = []
            for track_id in all_recommendations_list:
                f1 = track_id in contextual_recommendations
                f2 = track_id in recs_by_tracks
                f3 = track_id in dssm_recommendations

                if f1 + f2 + f3 == 3:
                    weights.append(3 * self._get_track_info(track_id).pop)
                elif f1 + f2 + f3 == 2:
                    weights.append(2 * self._get_track_info(track_id).pop)
                else:
                    weights.append(1 * self._get_track_info(track_id).pop)
            
            total_weight = sum(weights)
            normalized_weights = [weight / total_weight for weight in weights]

            chosen_track = random.choices(all_recommendations_list, weights=normalized_weights, k=1)[0]
            return chosen_track

        if contextual_recommendations:
            return max(contextual_recommendations, key=lambda track_id: self._get_track_info(track_id).pop)

        if self.top_tracks:
            return random.choice(self.top_tracks)

        return self.fallback.recommend_next(user, prev_track, prev_track_time)
