from random import random, choice
from typing import Optional

from .recommender import Recommender


class IndexedOrderedWithLikedArtists(Recommender):
    def __init__(self, recommendations_redis, tracks_redis, artists_redis, catalog, fallback):
        self.recommendations_redis = recommendations_redis
        self.tracks_redis = tracks_redis
        self.artists_redis = artists_redis
        self.fallback = fallback
        self.catalog = catalog
        self.liked_artists = dict()


    def __get_liked_artists(self, user: int):
        if user not in self.liked_artists:
            self.liked_artists[user] = set()
        return self.liked_artists[user]


    def __add_to_liked_artists(self, user: int, artist: int):
        if user not in self.liked_artists:
            self.liked_artists[user] = set()
        self.liked_artists[user].add(artist)


    def __recommend_for_liked_artists(self, user: int) -> Optional[int]:
        liked_artists_tracks = list()

        for artist in self.__get_liked_artists(user):
            artist_data = self.artists_redis.get(artist)
            artist_tracks = self.catalog.from_bytes(artist_data)

            liked_artists_tracks.extend(artist_tracks)

        # function will always be entered with a non-empty set of liked artists
        # so this line will never throw an error
        return choice(liked_artists_tracks)


    def recommend_next(self, user: int, prev_track: int, prev_track_time: float) -> int:
        if prev_track_time > 0.8:
            track_data = self.tracks_redis.get(prev_track)
            if track_data is not None:
                track = self.catalog.from_bytes(track_data)
            else:
                raise ValueError(f"Track not found: {prev_track}")

            if self.artists_redis.get(track.artist) is not None:
                self.__add_to_liked_artists(user, track.artist)

        recommendations_data = self.recommendations_redis.get(user)

        # should not happen too often
        if recommendations_data is None:
            return self.fallback.recommend_next(user, prev_track, prev_track_time)

        recommendations = list(self.catalog.from_bytes(recommendations_data))

        # possibly previous recommendation was from "liked artists"
        if prev_track not in recommendations:
            if prev_track_time > 0.8:
                return self.__recommend_for_liked_artists(user)
            else:
                return recommendations[0]

        rec_index = recommendations.index(prev_track)

        # previous track was recommended, if the user did not like it
        # try to recommend someone from "probably" liked artists
        if len(self.__get_liked_artists(user)) >= 3 and prev_track_time < 0.5:
            return self.__recommend_for_liked_artists(user)

        # continue taking from recommendations
        return recommendations[(rec_index + 1) % len(recommendations)]
