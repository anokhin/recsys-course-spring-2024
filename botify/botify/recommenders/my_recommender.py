from .recommender import Recommender


class MyRecommender(Recommender):
    def __init__(self, dssm_redis, gcf_redis, catalog, fallback, used, combined_tracks_set):
        self.dssm_redis = dssm_redis
        self.gcf_redis = gcf_redis
        self.catalog = catalog
        self.fallback = fallback
        self.used = used
        self.combined_tracks_set = combined_tracks_set
        self.weights = [0.52, 0.48]

    def get_combined_tracks(self, dssm_recommendations, gcf_recommendations, user):
        combined_tracks = []
        count = 0
        for track_dssm, track_gcf in zip(dssm_recommendations, gcf_recommendations):
            count += 1
            track_dssm_rank = self.weights[0] * 1 / count
            track_gcf_rank = self.weights[1] * 1 / count

            combined_tracks.append((track_dssm, track_dssm_rank))
            combined_tracks.append((track_gcf, track_gcf_rank))

        combined_tracks.sort(key=lambda x: x[1], reverse=True)

        self.combined_tracks_set.set(user, self.catalog.to_bytes(combined_tracks))
        return combined_tracks

    def recommend_next(self, user: int, prev_track: int, prev_track_time: float) -> int:
        recommendations_dssm = self.dssm_redis.get(user)
        recommendations_gcf = self.gcf_redis.get(user)

        if recommendations_gcf is not None and recommendations_dssm is not None:
            dssm_recommendations = list(self.catalog.from_bytes(recommendations_dssm))
            gcf_recommendations = list(self.catalog.from_bytes(recommendations_gcf))

            combined_tracks = self.combined_tracks_set.get(user)
            if combined_tracks is not None:
                combined_tracks = list(self.catalog.from_bytes(combined_tracks))
            else:
                combined_tracks = self.get_combined_tracks(dssm_recommendations, gcf_recommendations, user)

            used = self.used.get(user)
            if used is not None:
                used = list(self.catalog.from_bytes(used))
            else:
                used = []

            ind_next_track = len(used)

            if ind_next_track >= len(combined_tracks):
                return self.fallback.recommend_next(user, prev_track, prev_track_time)

            used.append(combined_tracks[ind_next_track][0])
            self.used.set(user, self.catalog.to_bytes(used))
            return combined_tracks[ind_next_track][0]

        else:
            return self.fallback.recommend_next(user, prev_track, prev_track_time)
