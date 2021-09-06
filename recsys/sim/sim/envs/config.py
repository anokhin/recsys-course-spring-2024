from dataclasses import dataclass

import marshmallow_dataclass


@dataclass()
class SongCatalogConfig:
    size: int


@dataclass
class UserConfig:
    user: int
    song_catalog_config: SongCatalogConfig


@dataclass
class RecEnvConfig:
    song_catalog_config: SongCatalogConfig
    user_base_size: int


RecEnvConfigSchema = marshmallow_dataclass.class_schema(RecEnvConfig)
