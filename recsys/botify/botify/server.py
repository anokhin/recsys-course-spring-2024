import json
import logging
from dataclasses import asdict

from flask import Flask
from flask_redis import Redis
from flask_restful import Resource, Api, abort, reqparse

from botify.track import Catalog

root = logging.getLogger()
root.setLevel("INFO")

app = Flask(__name__)
app.config.from_file("config.json", load=json.load)
api = Api(app)
redis = Redis(app)

catalog = Catalog(app).load(app.config["TRACKS_CATALOG"])
catalog.upload(redis.connection)

parser = reqparse.RequestParser()
parser.add_argument("track", type=int, location="form", required=True)
parser.add_argument("time", type=float, location="form", required=True)


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
        app.logger.info(
            f"User {user} listened to the track {args.track} for {args.time}; recommending track {recommendation}"
        )
        return {"user": user, "track": recommendation}


api.add_resource(Hello, "/")
api.add_resource(Track, "/track/<int:track>")
api.add_resource(NextTrack, "/next/<int:user>")


if __name__ == "__main__":
    app.run(host="0.0.0.0")
