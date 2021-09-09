import faiss
import numpy as np

from sim.envs.config import TrackCatalogConfig


class TrackCatalog:
    def __init__(self, config: TrackCatalogConfig):
        self.config = config
        self.track_embeddings = np.load(config.track_embeddings_path)
        self.index = self.build_track_index()

    def build_track_index(self) -> faiss.Index:
        index = faiss.index_factory(
            self.track_embeddings.shape[1], "Flat", faiss.METRIC_INNER_PRODUCT
        )
        index.add(self.track_embeddings)
        return index

    def get_embedding(self, track):
        return self.track_embeddings[track]

    def get_nearest(self, query, k):
        dist, ind = self.index.search(query[np.newaxis, :], k)
        return ind

    def size(self):
        return self.track_embeddings.shape[0]
