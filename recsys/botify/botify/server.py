import json
import logging
from dataclasses import asdict
from datetime import datetime

from flask import Flask
from flask_redis import Redis
from flask_restful import Resource, Api, abort, reqparse

from botify.data import DataLogger, Datum
from botify.track import Catalog

root = logging.getLogger()
root.setLevel("INFO")

app = Flask(__name__)
app.config.from_file("config.json", load=json.load)
api = Api(app)
redis = Redis(app)
data_logger = DataLogger(app)

catalog = Catalog(app).load(app.config["TRACKS_CATALOG"])
catalog.upload(redis.connection)

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
        data = redis.connection.get(track)
        if data is not None:
            return asdict(catalog.track_from_bytes(data))
        else:
            abort(404, description="Track not found")


class NextTrack(Resource):
    def post(self, user: int):
        args = parser.parse_args()
        recommendation = int(redis.connection.randomkey())
        data_logger.log(
            "next",
            Datum(
                int(datetime.now().timestamp()),
                user,
                args.track,
                args.time,
                recommendation,
            ),
        )
        return {"user": user, "track": recommendation}


class LastTrack(Resource):
    def post(self, user: int):
        args = parser.parse_args()
        data_logger.log(
            "last", Datum(int(datetime.now().timestamp()), user, args.track, args.time),
        )
        return {"user": user}


api.add_resource(Hello, "/")
api.add_resource(Track, "/track/<int:track>")
api.add_resource(NextTrack, "/next/<int:user>")
api.add_resource(LastTrack, "/last/<int:user>")


if __name__ == "__main__":
    app.run(host="0.0.0.0")
