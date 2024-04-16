import random
import pickle

from .recommender import Recommender


class BadEnsemble(Recommender):
    def __init__(
        self,
        recommendations_dssm,
        recommendations_top_lfm,
        recommendations_lfm,
        recommendations_contextual,
        catalog,
        fallback,
    ):
        self.recommendations_dssm = recommendations_dssm
        self.recommendations_contextual = recommendations_contextual
        self.recommendations_top_lfm = recommendations_top_lfm
        self.recommendations_lfm = recommendations_lfm
        self.fallback = fallback
        self.catalog = catalog
        
        self.dssm_weight = 0.4
        self.top_lfm_weight = 0.5
        self.lfm_weight = 0.1
        
        self.topk = 5

    def recommend_next(
        self,
        user: int,
        prev_track: int,
        prev_track_time: float,
    ) -> int:
        recommendations_dssm = self.recommendations_dssm.get(user)
        previous_track = self.recommendations_contextual.get(prev_track)
        recommendations_top_lfm = self.recommendations_top_lfm.get(user)
        recommendations_lfm = self.recommendations_lfm.get(user)
        data = {}

        if previous_track is not None:
            recommendations = list(self.catalog.from_bytes(previous_track))
            for value in recommendations:
                data[value] = data.get(value, 0) + prev_track_time
                
        if recommendations_dssm is not None:
            recommendations = list(self.catalog.from_bytes(previous_track))
            for value in recommendations:
                data[value] = data.get(value, 0) + prev_track_time
                
        if recommendations_top_lfm is not None:
            recommendations = list(self.catalog.from_bytes(recommendations_top_lfm))
            for value in recommendations:
                data[value] = data.get(value, 0) + self.top_lfm_weight
                
        if recommendations_lfm is not None:
            recommendations = list(self.catalog.from_bytes(recommendations_lfm))
            for value in recommendations:
                data[value] = data.get(value, 0) + self.lfm_weight
        
        if not data:
            return self.fallback.recommend_next(
                user, prev_track, prev_track_time)
        top_data = random.sample(list(data.keys()), 5)
        return max(top_data, key=data.get)
    
    
class Ensemble(Recommender):
    def __init__(
        self,
        recommendations_dssm,
        recommendations_top_lfm,
        recommendations_lfm,
        catalog,
        fallback,
    ):
        self.recommendations_dssm = recommendations_dssm
        self.recommendations_top_lfm = recommendations_top_lfm
        self.recommendations_lfm = recommendations_lfm
        self.fallback = fallback
        self.catalog = catalog
        
        self.threshold_dssm = 0.4
        self.top_lfm_weight = 0.7
        self.lfm_weight = 0.3
        self.topk = 5
        self.shift = 1

    def recommend_next(
        self,
        user: int,
        prev_track: int,
        prev_track_time: float,
    ) -> int:
        recommendations_dssm = self.recommendations_dssm.get(user)
        recommendations_top_lfm = self.recommendations_top_lfm.get(user)
        recommendations_lfm = self.recommendations_lfm.get(user)
        
        if recommendations_dssm is None and recommendations_lfm is None and recommendations_top_lfm is None:
            return self.fallback.recommend_next(user, prev_track, prev_track_time)
            
        if prev_track_time < self.threshold_dssm or recommendations_dssm is None:
            data_lfm = {}
            if recommendations_lfm is not None:
                recommendations = list(self.catalog.from_bytes(recommendations_lfm))
                for i, value in enumerate(recommendations):
                    data_lfm[value] = self.lfm_weight * (len(recommendations) - i)
            if recommendations_top_lfm is not None:
                recommendations = list(self.catalog.from_bytes(recommendations_top_lfm))
                for value in recommendations:
                    data_lfm[value] = self.top_lfm_weight * (len(recommendations) - i)
            top_data = random.sample(list(data_lfm.keys()), self.topk)
            return max(top_data, key=data_lfm.get)
                
        recommendations = list(self.catalog.from_bytes(recommendations_dssm))
        if prev_track in recommendations:
            index = recommendations.index(prev_track)
            top_recommendations = recommendations[max(0, index - self.shift):index]
            top_recommendations += top_recommendations[index + 1: min(index + self.shift + 1, len(recommendations))]
            random.shuffle(top_recommendations)
            if top_recommendations:
                return top_recommendations[0]
        random.shuffle(recommendations)
        return recommendations[0]
        
