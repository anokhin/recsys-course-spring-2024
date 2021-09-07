import json
import logging
from dataclasses import asdict

from flask import Flask
from flask_redis import Redis
from flask_restful import Resource, Api, abort

from dodify.track import Catalog

root = logging.getLogger()
root.setLevel("INFO")

app = Flask(__name__)
app.config.from_file("config.json", load=json.load)
api = Api(app)
redis = Redis(app)

catalog = Catalog(app).load(app.config["TRACKS_CATALOG"])
catalog.upload(redis.connection)


class Hello(Resource):
    def get(self):
        return {
            "status": "alive",
            "message": "welcome to dodify, the best toy music recommender",
        }


class Track(Resource):
    def get(self, track: int):
        data = redis.connection.get(track)
        if data is not None:
            return asdict(catalog.track_from_bytes(data))
        else:
            abort(404, description="Track not found")


class NextTrack(Resource):
    def get(self, user: int):
        return {"user": user, "track": int(redis.connection.randomkey())}


api.add_resource(Hello, "/")
api.add_resource(Track, "/track/<int:track>")
api.add_resource(NextTrack, "/next/<int:user>")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
