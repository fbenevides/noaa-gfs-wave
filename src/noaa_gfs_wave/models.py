"""Pydantic domain models — stub."""

from pydantic import BaseModel


class Wind10m(BaseModel):
    pass


class CombinedSea(BaseModel):
    pass


class DominantSystem(BaseModel):
    pass


class WindSea(BaseModel):
    pass


class SwellPartition(BaseModel):
    pass


class WW3PointMeta(BaseModel):
    pass


class WW3PointForecast(BaseModel):
    pass
