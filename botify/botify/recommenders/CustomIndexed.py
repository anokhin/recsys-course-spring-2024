import random

from .recommender import Recommender




class CustomIndexed(Recommender):
    def __init__(self, recommendations_redis, catalog, fallback, track2author):
        self.recommendations_redis = recommendations_redis
        self.fallback = fallback
        self.catalog = catalog
        self.track2author = track2author
        self.probas = {}
        self.rand = random.Random()

    def random_choice(self, lst, size=1, probabilities=None):
        if probabilities is None:
            probabilities = [1 / len(lst)] * len(lst)

        if sum(probabilities) != 1:
            probabilities = [p / sum(probabilities) for p in probabilities]

        choices = []
        for _ in range(size):
            rand_num = self.rand.random()
            current_cumulative_prob = 0
            for i, prob in enumerate(probabilities):
                current_cumulative_prob += prob
                if rand_num < current_cumulative_prob:
                    choices.append(lst[i])
                    break

        return choices[0]

    def recommend_next(self, user: int, prev_track: int, prev_track_time: float) -> int:
        recommendations = self.recommendations_redis.get(user)

        if recommendations is not None:
            arr = list(self.catalog.from_bytes(recommendations))
            if user not in self.probas:
                p = self._get_probas(arr, prev_track)
                self.probas[user] = p
            probs = self.probas[user]
            self._update_probas(arr, prev_track, probs)

            return self.random_choice(arr, probabilities=probs)
        else:
            return self.fallback.recommend_next(user, prev_track, prev_track_time)

    def _get_probas(self, recs, prev_track):
        n = len(recs)
        tmp = [(i + 1) for i in range(n)]
        s_tmp = sum(tmp)
        tmp.reverse()
        p = [e / s_tmp for e in tmp]

        return p

    def _update_probas(self, recs, prev_track, p):
        prev_author = self.track2author[prev_track]
        for idx, track in enumerate(recs):
            cur_author = self.track2author[track]
            if track == prev_track:
                p[idx] = 0.0
            elif prev_author == cur_author:
                p[idx] *= 0.95
