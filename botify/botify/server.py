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
recommendations_ub = Redis(app, config_prefix="REDIS_RECOMMENDATIONS_UB")
recommendations_lfm = Redis(app, config_prefix="REDIS_RECOMMENDATIONS")
recommendations_dssm = Redis(app, config_prefix="REDIS_RECOMMENDATIONS_DSSM")
recommendations_contextual = Redis(app, config_prefix="REDIS_RECOMMENDATIONS_CONTEXTUAL")
recommendations_gcf = Redis(app, config_prefix="REDIS_RECOMMENDATIONS_GCF")
recommendations_div = Redis(app, config_prefix="REDIS_TRACKS_WITH_DIVERSE_RECS")

data_logger = DataLogger(app)

catalog = Catalog(app).load(app.config["TRACKS_CATALOG"])
catalog.upload_tracks(tracks_redis.connection)
catalog.upload_artists(artists_redis.connection)
catalog.upload_recommendations(
    recommendations_ub.connection, "RECOMMENDATIONS_UB_FILE_PATH"
)
catalog.upload_recommendations(
    recommendations_lfm.connection, "RECOMMENDATIONS_FILE_PATH"
)
catalog.upload_recommendations(
    recommendations_dssm.connection, "RECOMMENDATIONS_DSSM_FILE_PATH"
)
catalog.upload_recommendations(
    recommendations_contextual, "RECOMMENDATIONS_CONTEXTUAL_FILE_PATH",
    key_object='track', key_recommendations='recommendations'
)
catalog.upload_recommendations(
    recommendations_gcf, "RECOMMENDATIONS_GCF_FILE_PATH"
)
catalog.upload_recommendations(
    recommendations_div, "TRACKS_WITH_DIVERSE_RECS_CATALOG_FILE_PATH",
    key_object='track', key_recommendations='recommendations'
)

top_tracks = TopPop.load_from_json(app.config["TOP_TRACKS"])

parser = reqparse.RequestParser()
parser.add_argument("track", type=int, location="json", required=True)
parser.add_argument("time", type=float, location="json", required=True)


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

        treatment = Experiments.ALL.assign(user)

        if treatment == Treatment.T1:
            recommender = StickyArtist(tracks_redis.connection, artists_redis.connection, catalog)
        elif treatment == Treatment.T2:
            recommender = TopPop(catalog.top_tracks[:100], Random(tracks_redis.connection))
        elif treatment == Treatment.T3:
            recommender = Indexed(recommendations_lfm.connection, catalog, Random(tracks_redis.connection))
        elif treatment == Treatment.T4:
            recommender = Indexed(recommendations_dssm.connection, catalog, Random(tracks_redis.connection))
        elif treatment == Treatment.T5:
            recommender = Contextual(recommendations_contextual.connection, catalog, Random(tracks_redis.connection))
        elif treatment == Treatment.T6:
            recommender = Contextual(recommendations_div.connection, catalog, Random(tracks_redis.connection))
        else:
            recommender = Random(tracks_redis.connection)

        recommendation = recommender.recommend_next(user, args.track, args.time)

        data_logger.log(
            "next",
            Datum(
                int(datetime.now().timestamp() * 1000),
                user,
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
        data_logger.log(
            "last",
            Datum(
                int(datetime.now().timestamp() * 1000),
                user,
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
