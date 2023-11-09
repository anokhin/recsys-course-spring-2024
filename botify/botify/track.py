import itertools
import json
import pickle
from dataclasses import dataclass, field
from typing import List


@dataclass
class Track:
    track: int
    artist: str
    title: str
    recommendations: List[int] = field(default=lambda: [])


class Catalog:
    """
    A helper class used to load track data upon server startup
    and store the data to redis.
    """

    def __init__(self, app):
        self.app = app
        self.tracks = []
        self.top_tracks = []
        self.tracks_with_diverse_recs = []

    # TODO Seminar 8 step 1: Configure reading tracks with diverse recommendations
    def load(self, catalog_path, tracks_with_diverse_recs_path):
        self.app.logger.info(f"Loading tracks from {catalog_path}")
        with open(catalog_path) as catalog_file:
            for j, line in enumerate(catalog_file):
                data = json.loads(line)
                self.tracks.append(
                    Track(
                        data["track"],
                        data["artist"],
                        data["title"],
                        data.get("recommendations", []),
                    )
                )
        self.app.logger.info(f"Loaded {j + 1} tracks")

        self.app.logger.info(f"Loading tracks with diverse recommendations from {tracks_with_diverse_recs_path}")

        # your code is here
        with open(tracks_with_diverse_recs_path) as tracks_with_diverse_recs_file:
            for j, line in enumerate(tracks_with_diverse_recs_file):
                data = json.loads(line)
                self.tracks_with_diverse_recs.append(
                    Track(
                        data["track"],
                        data["artist"],
                        data["title"],
                        data.get("recommendations", []),
                    )
                )

        self.app.logger.info(f"Loaded {j + 1} tracks with diverse recs")
        return self

    # TODO Seminar 8 step 2: Configure uploading tracks with diverse recommendations to redis DB
    def upload_tracks(self, redis_tracks, redis_tracks_with_diverse_recs):
        self.app.logger.info(f"Uploading tracks to redis")
        for track in self.tracks:
            redis_tracks.set(track.track, self.to_bytes(track))

        for track in self.tracks_with_diverse_recs:
            redis_tracks_with_diverse_recs.set(track.track, self.to_bytes(track))

        self.app.logger.info(
            f"Uploaded {len(self.tracks)} tracks, {len(self.tracks_with_diverse_recs)} tracks with diverse recs"
        )

    def upload_artists(self, redis):
        self.app.logger.info(f"Uploading artists to redis")
        sorted_tracks = sorted(self.tracks, key=lambda track: track.artist)
        for j, (artist, artist_catalog) in enumerate(
            itertools.groupby(sorted_tracks, key=lambda track: track.artist)
        ):
            artist_tracks = [t.track for t in artist_catalog]
            redis.set(artist, self.to_bytes(artist_tracks))

        self.app.logger.info(f"Uploaded {j + 1} artists")

    def upload_recommendations(
        self, redis, recommendations_path="RECOMMENDATIONS_FILE_PATH"
    ):
        recommendations_file_path = self.app.config[recommendations_path]

        self.app.logger.info(
            f"Uploading recommendations to redis from {recommendations_file_path}"
        )

        j = 0
        with open(recommendations_file_path) as rf:
            for line in rf:
                recommendations = json.loads(line)
                redis.set(
                    recommendations["user"], self.to_bytes(recommendations["tracks"])
                )
                j += 1
        self.app.logger.info(f"Uploaded recommendations for {j} users")

    def to_bytes(self, instance):
        return pickle.dumps(instance)

    def from_bytes(self, bts):
        return pickle.loads(bts)
