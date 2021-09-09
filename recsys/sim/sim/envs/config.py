from dataclasses import dataclass

import marshmallow_dataclass


@dataclass()
class TrackCatalogConfig:
    track_embeddings_path: str


@dataclass
class UserCatalogConfig:
    user_catalog_path: str


@dataclass()
class RemoteRecommenderConfig:
    host: str
    port: int


@dataclass
class RecEnvConfig:
    track_catalog_config: TrackCatalogConfig
    user_catalog_config: UserCatalogConfig
    remote_recommender_config: RemoteRecommenderConfig


RecEnvConfigSchema = marshmallow_dataclass.class_schema(RecEnvConfig)
