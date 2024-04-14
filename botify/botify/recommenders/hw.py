import random

from .recommender import Recommender
from .random import Random
from .contextual import Contextual

class HW(Recommender):
    def __init__(self, tracks_redis, artists_redis, catalog, recommendations_dssm, recommendations_contextual):
        self.fallback_contextual = Contextual(recommendations_contextual, catalog, Random(tracks_redis))
        self.recommendations_redis = recommendations_dssm
        self.tracks_redis = tracks_redis
        self.artists_redis = artists_redis
        self.catalog = catalog
        self.playlist_dict = {}
        self.artist_play_count = {}

    def track_to_playlist(self, user, track_id):
        if user in self.playlist_dict:
            self.playlist_dict[user].append(track_id)
        else:
            self.playlist_dict[user] = [track_id]

        track = self.catalog.from_bytes(self.tracks_redis.get(track_id))
        if user in self.artist_play_count:
            if track.artist in self.artist_play_count[user]:
                self.artist_play_count[user][track.artist] += 1
            else:
                self.artist_play_count[user][track.artist] = 1
        else:
            self.artist_play_count[user] = {track.artist: 1}

    def recommend_next(self, user: int, prev_track: int, prev_track_time: float) -> int:
        maxArtistTrack = 5

        recommendations = self.recommendations_redis.get(user)
        if recommendations is not None:
            trackList = list(self.catalog.from_bytes(recommendations))
            prev_track_idx = 0
            if prev_track in trackList:
                prev_track_idx = (trackList.index(prev_track) + 1) % len(trackList)
            for i in range(prev_track_idx, len(trackList)):
                rec_track = trackList[i]
                if user not in self.playlist_dict:
                    break
                if rec_track not in self.playlist_dict[user]:
                    track = self.catalog.from_bytes(self.tracks_redis.get(rec_track))
                    if track.artist not in self.artist_play_count[user]:
                        break
                    if self.artist_play_count[user][track.artist] < maxArtistTrack:
                        break
                rec_track = -1
        else:
            rec_track = -1

        if rec_track == -1 and prev_track_time >= 0.6:
            track_data = self.tracks_redis.get(prev_track)
            if track_data is not None:
                track = self.catalog.from_bytes(track_data)
                artist_data = self.artists_redis.get(track.artist)
                if artist_data is not None and user in self.artist_play_count and track.artist in self.artist_play_count[user] and self.artist_play_count[user][track.artist] < maxArtistTrack:
                    artist_tracks = self.catalog.from_bytes(artist_data)
                    if len(artist_tracks) > 1:
                        for i in range(len(artist_tracks)):
                            rec_track = artist_tracks[i]
                            if user not in self.playlist_dict or rec_track not in self.playlist_dict[user]:
                                break
                            rec_track = -1

        if rec_track == -1:
            rec_track = self.fallback_contextual.recommend_next(user, prev_track, prev_track_time)
        
            track = self.catalog.from_bytes(self.tracks_redis.get(rec_track))
            if (user in self.playlist_dict and rec_track in self.playlist_dict[user]) or (user in self.artist_play_count and track.artist in self.artist_play_count[user] and self.artist_play_count[user][track.artist] >= maxArtistTrack):
                while (rec_track in self.playlist_dict[user]) or (track.artist in self.artist_play_count[user] and self.artist_play_count[user][track.artist] >= maxArtistTrack):
                    rec_track = Random(self.tracks_redis).recommend_next(user, prev_track, prev_track_time)
                    track = self.catalog.from_bytes(self.tracks_redis.get(rec_track))

        self.track_to_playlist(user, rec_track)
        return rec_track
