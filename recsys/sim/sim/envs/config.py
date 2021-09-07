from dataclasses import dataclass

import marshmallow_dataclass


@dataclass()
class RemoteRecommenderConfig:
    host: str
    port: int


@dataclass()
class TrackCatalogConfig:
    size: int


@dataclass
class UserConfig:
    user: int
    track_catalog_config: TrackCatalogConfig


@dataclass
class RecEnvConfig:
    track_catalog_config: TrackCatalogConfig
    user_base_size: int
    remote_recommender_config: RemoteRecommenderConfig


RecEnvConfigSchema = marshmallow_dataclass.class_schema(RecEnvConfig)
