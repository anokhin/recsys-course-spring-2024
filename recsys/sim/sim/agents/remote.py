import requests
from typing import Dict

from .recommender import Recommender
from ..envs import RemoteRecommenderConfig

from urllib.parse import urlunsplit, urlencode

SCHEME = "http"


class RemoteRecommender(Recommender):
    """Call the remote recommender service"""

    def __init__(self, config: RemoteRecommenderConfig):
        self.host = config.host
        self.port = config.port

    def recommend(self, observation: Dict[str, int], reward: float, done: bool) -> int:
        query_params = {"track": observation["track"]} if "track" in observation else {}
        url = self.get_request_url(f"next/{observation['user']}", query_params)
        response = requests.get(url)
        return response.json()["track"]

    def get_request_url(self, path, query_params):
        query = urlencode(query_params)
        return urlunsplit((SCHEME, f"{self.host}:{self.port}", path, query, ""))

    def __repr__(self):
        return f"remote({self.host}, {self.port})"
