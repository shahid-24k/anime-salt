from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Source:
    language: str
    url: str
    server: Optional[str] = None
    quality: Optional[str] = None


@dataclass
class Episode:
    number: int
    title: Optional[str] = None
    sources: List[Source] = field(default_factory=list)


@dataclass
class Season:
    number: int
    episodes: List[Episode] = field(default_factory=list)


@dataclass
class Anime:
    canonical_id: str
    title: str
    alternate_titles: List[str] = field(default_factory=list)
    genres: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    image: Optional[str] = None
    popularity: Optional[int] = None
    trending: Optional[int] = None
    seasons: List[Season] = field(default_factory=list)
