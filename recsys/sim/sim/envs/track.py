import numpy as np

from sim.envs.config import TrackCatalogConfig


class TrackCatalog:
    def __init__(self, config: TrackCatalogConfig):
        self.config = config
        self.track_embeddings = np.load(config.track_embeddings_path)

    def size(self):
        return self.track_embeddings.shape[0]
