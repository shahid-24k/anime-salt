import base64
import json
import re
from urllib.parse import unquote

import requests

from app.models import Anime, Season, Episode, Source


class AnimeSaltProvider:
    BASE_URL = "https://animesalt.link"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0"
        })

    def get_episode(self, slug):
        url = f"{self.BASE_URL}/episode/{slug}/"
        response = self.session.get(url, timeout=20)
        response.raise_for_status()
        return response.text

    def parse_episode(self, slug):
        html = self.get_episode(slug)

        title_match = re.search(
            r"<h1[^>]*>(.*?)</h1>",
            html,
            re.IGNORECASE | re.DOTALL
        )

        title = (
            re.sub(r"<[^>]+>", "", title_match.group(1)).strip()
            if title_match
            else None
        )

        episode_match = re.search(
            r"Season\s+(\d+)\s+Episode\s+(\d+)",
            html,
            re.IGNORECASE
        )

        season_number = (
            int(episode_match.group(1))
            if episode_match
            else None
        )

        episode_number = (
            int(episode_match.group(2))
            if episode_match
            else None
        )

        sources = [
            Source(
                language=item["language"],
                url=item["link"]
            )
            for item in self.extract_languages(html)
        ]

        return Episode(
            number=episode_number,
            title=title,
            sources=sources
        )

    def extract_languages(self, html):
        pattern = (
            r"https://animesalt\.link/"
            r"multi-lang-plyr/player\.php\?data=([^\"'&]+)"
        )

        match = re.search(pattern, html, re.IGNORECASE)

        if not match:
            return []

        encoded = unquote(match.group(1))

        try:
            decoded = base64.b64decode(encoded).decode("utf-8")
            entries = json.loads(decoded)
        except (
            ValueError,
            UnicodeDecodeError,
            json.JSONDecodeError
        ):
            return []

        return [
            {
                "language": entry.get("language"),
                "link": entry.get("link")
            }
            for entry in entries
            if entry.get("language") and entry.get("link")
        ]

    def get_anime(self, slug):
        episode = self.parse_episode(f"{slug}-1x1")

        season = Season(
            number=1,
            episodes=[episode]
        )

        return Anime(
            canonical_id=f"animesalt:{slug}",
            title=episode.title or slug,
            seasons=[season]
        )
