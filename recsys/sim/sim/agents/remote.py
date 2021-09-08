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
        data = {"track": observation["track"], "time": reward}
        url = self.get_request_url(f"next/{observation['user']}", {})
        response = requests.post(url, data=data)
        return response.json()["track"]

    def get_request_url(self, path, query_params):
        query = urlencode(query_params)
        return urlunsplit((SCHEME, f"{self.host}:{self.port}", path, query, ""))

    def __repr__(self):
        return f"remote({self.host}, {self.port})"
