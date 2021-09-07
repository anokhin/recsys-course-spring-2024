from dataclasses import dataclass

import marshmallow_dataclass


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


RecEnvConfigSchema = marshmallow_dataclass.class_schema(RecEnvConfig)
