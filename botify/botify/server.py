import json
import logging
import time
from dataclasses import asdict
from datetime import datetime

from flask import Flask
from flask_redis import Redis
from flask_restful import Resource, Api, abort, reqparse
from gevent.pywsgi import WSGIServer

from botify.data import DataLogger, Datum
from botify.experiment import Experiments, Treatment
from botify.recommenders.Indexed import Indexed
from botify.recommenders.final import Final
from botify.recommenders.different_artist import DifferentArtist
from botify.recommenders.random import Random
from botify.recommenders.contextual import Contextual
from botify.recommenders.toppop import TopPop
from botify.recommenders.sticky_artist import StickyArtist
from botify.track import Catalog

root = logging.getLogger()
root.setLevel("INFO")

app = Flask(__name__)
app.config.from_file("config.json", load=json.load)
api = Api(app)

tracks_redis = Redis(app, config_prefix="REDIS_TRACKS")
artists_redis = Redis(app, config_prefix="REDIS_ARTIST")
sessions_redis = Redis(app, config_prefix="REDIS_SESSIONS")
recommendations_dssm = Redis(app, config_prefix="REDIS_RECOMMENDATIONS_DSSM")
recommendations_final = Redis(app, config_prefix="REDIS_RECOMMENDATIONS_FINAL")

data_logger = DataLogger(app)

catalog = Catalog(app).load(app.config["TRACKS_CATALOG"])
catalog.upload_tracks(tracks_redis.connection)
catalog.upload_artists(artists_redis.connection)
catalog.upload_recommendations(
    recommendations_dssm.connection, "RECOMMENDATIONS_DSSM_FILE_PATH"
)
catalog.upload_recommendations(
    recommendations_final.connection, "RECOMMENDATIONS_FINAL_FILE_PATH"
)

parser = reqparse.RequestParser()
parser.add_argument("track", type=int, location="json", required=True)
parser.add_argument("time", type=float, location="json", required=True)
parser.add_argument("session_id", type=int, location="json", required=True)


class Hello(Resource):
    def get(self):
        return {
            "status": "alive",
            "message": "welcome to botify, the best toy music recommender",
        }


class Track(Resource):
    def get(self, track: int):
        data = tracks_redis.connection.get(track)
        if data is not None:
            return asdict(catalog.from_bytes(data))
        else:
            abort(404, description="Track not found")


class NextTrack(Resource):
    def post(self, user: int):
        start = time.time()

        args = parser.parse_args()

        treatment = Experiments.FINAL.assign(user)
        # treatment = Experiments.AA.assign(user)

        if treatment == Treatment.T1:
            recommender = Final(
                recommendations_final.connection, sessions_redis.connection, tracks_redis.connection,
                catalog, Random(tracks_redis.connection),
            )
            # recommender = DifferentArtist(tracks_redis.connection, sessions_redis.connection)
        else:
            recommender = Indexed(recommendations_dssm.connection, catalog, Random(tracks_redis.connection))
            # recommender = DifferentArtist(tracks_redis.connection, sessions_redis.connection)

        recommendation = recommender.recommend_next(user, args.session_id, args.track, args.time)

        data_logger.log(
            "next",
            Datum(
                int(datetime.now().timestamp() * 1000),
                user,
                args.session_id,
                args.track,
                args.time,
                time.time() - start,
                recommendation,
            ),
        )
        return {"user": user, "track": recommendation}


class LastTrack(Resource):
    def post(self, user: int):
        start = time.time()
        args = parser.parse_args()
        sessions_redis.connection.delete(args.session_id)
        data_logger.log(
            "last",
            Datum(
                int(datetime.now().timestamp() * 1000),
                user,
                args.session_id,
                args.track,
                args.time,
                time.time() - start,
            ),
        )
        return {"user": user}


api.add_resource(Hello, "/")
api.add_resource(Track, "/track/<int:track>")
api.add_resource(NextTrack, "/next/<int:user>")
api.add_resource(LastTrack, "/last/<int:user>")

app.logger.info(f"Botify service stared")

if __name__ == "__main__":
    http_server = WSGIServer(("", 5001), app)
    http_server.serve_forever()
