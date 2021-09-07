from typing import Dict

from .recommender import Recommender


class RemoteRecommender(Recommender):
    """Call the remote recommender service"""

    def __init__(self):
        pass

    def recommend(self, observation: Dict[str, int], reward: float, done: bool) -> int:
        raise NotImplementedError()

    def __repr__(self):
        return "remote"
