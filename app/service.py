import requests

from app.models import Anime, Season, Episode, Source
from app.sources.anilist import AniListProvider


class AnimeService:
    ANIVEXA_URL = "https://anivexa-api.vercel.app"

    def __init__(self):
        self.anilist = AniListProvider()

        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Anime-VLC/1.0",
            "Accept": "application/json",
        })

    def search(self, query):
        return self.anilist.search(query)

    def get_episode_data(self, anilist_id):
        response = self.session.get(
            f"{self.ANIVEXA_URL}/episodes/{anilist_id}",
            timeout=30,
        )

        response.raise_for_status()

        data = response.json()

        if not isinstance(data, dict):
            raise ValueError("Invalid episode API response")

        return data

    def _extract_provider_episodes(self, provider_data):
        if not isinstance(provider_data, dict):
            return []

        episodes = provider_data.get("episodes")

        if not isinstance(episodes, dict):
            return []

        output = []

        for language in ("sub", "dub"):
            items = episodes.get(language, [])

            if not isinstance(items, list):
                continue

            for item in items:
                if not isinstance(item, dict):
                    continue

                output.append({
                    "language": language.upper(),
                    "number": item.get("number"),
                    "title": item.get("title"),
                    "id": item.get("id"),
                })

        return output

    def _collect_episode_providers(self, data, episode_number):
        providers = []

        for provider_name, provider_data in data.items():
            if not isinstance(provider_data, dict):
                continue

            for item in self._extract_provider_episodes(provider_data):
                try:
                    number = int(item.get("number") or 0)
                except (TypeError, ValueError):
                    continue

                if number != episode_number:
                    continue

                episode_id = item.get("id")

                if not episode_id:
                    continue

                providers.append({
                    "provider": provider_name,
                    "language": item["language"],
                    "id": episode_id,
                })

        return providers

    def get_anime(self, query):
        results = self.anilist.search(query)

        if not results:
            return None

        result = results[0]
        title_data = result.get("title", {})

        title = (
            title_data.get("english")
            or title_data.get("romaji")
            or title_data.get("native")
            or query
        )

        anime_id = result["id"]

        anime = Anime(
            canonical_id=f"anilist:{anime_id}",
            title=title,
            alternate_titles=[
                value
                for value in (
                    title_data.get("english"),
                    title_data.get("romaji"),
                    title_data.get("native"),
                )
                if value and value != title
            ],
            genres=result.get("genres", []),
            image=result.get("coverImage", {}).get("large"),
            popularity=result.get("popularity"),
        )

        try:
            data = self.get_episode_data(anime_id)
        except requests.RequestException as exc:
            print(f"Episode API request failed: {exc}")
            anime.seasons.append(Season(number=1))
            return anime

        season = Season(number=1)
        episode_count = result.get("episodes") or 0

        for episode_number in range(1, episode_count + 1):

            provider_ids = self._collect_episode_providers(
                data,
                episode_number,
            )

            if not provider_ids:
                continue

            title = None

            for provider_data in data.values():
                if not isinstance(provider_data, dict):
                    continue

                for item in self._extract_provider_episodes(
                    provider_data
                ):
                    try:
                        number = int(item.get("number") or 0)
                    except (TypeError, ValueError):
                        continue

                    if number == episode_number:
                        title = item.get("title")
                        break

                if title:
                    break

            season.episodes.append(
                Episode(
                    number=episode_number,
                    title=title,
                    sources=[],
                    provider_ids=provider_ids,
                )
            )

        anime.seasons.append(season)

        return anime
