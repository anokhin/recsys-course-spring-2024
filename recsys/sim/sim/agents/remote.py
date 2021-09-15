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
        data = {"track": int(observation["track"]), "time": reward}
        endpoint = "next" if not done else "last"
        url = self.get_request_url(f"{endpoint}/{observation['user']}", {})
        response = requests.post(url, json=data)
        return response.json().get("track")

    def get_request_url(self, path, query_params):
        query = urlencode(query_params)
        return urlunsplit((SCHEME, f"{self.host}:{self.port}", path, query, ""))

    def __repr__(self):
        return f"remote({self.host}, {self.port})"
