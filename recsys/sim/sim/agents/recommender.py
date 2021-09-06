from typing import Dict


class Recommender(object):
    def recommend(self, observation: Dict[str, int], reward: float, done: bool) -> int:
        raise NotImplementedError()
