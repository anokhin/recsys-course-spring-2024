from sim.envs.config import TrackCatalogConfig


class TrackCatalog:

    def __init__(self, config: TrackCatalogConfig):
        self.config = config

    def size(self):
        return self.config.size
