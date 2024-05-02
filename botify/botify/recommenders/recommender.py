class Recommender:
    def recommend_next(self, user: int, session_id: int, prev_track: int, prev_track_time: float) -> int:
        raise NotImplementedError()
