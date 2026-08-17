from app.models import Anime, Season
from app.sources.anilist import AniListProvider
from app.sources.animesalt import AnimeSaltProvider


class AnimeService:

    def __init__(self):
        self.anilist = AniListProvider()
        self.animesalt = AnimeSaltProvider()

    def search(self, query):
        return self.anilist.search(query)

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

        anime = Anime(
            canonical_id=f"anilist:{result['id']}",
            title=title,
            alternate_titles=[
                value
                for value in [
                    title_data.get("english"),
                    title_data.get("romaji"),
                    title_data.get("native")
                ]
                if value and value != title
            ],
            genres=result.get("genres", []),
            image=result.get("coverImage", {}).get("large"),
            popularity=result.get("popularity"),
        )

        episode_count = result.get("episodes") or 0

        # Convert title to the source's normal slug format.
        slug = title.lower()

        import re
        slug = re.sub(r"[^a-z0-9]+", "-", slug).strip("-")

        season = Season(number=1)

        for episode_number in range(1, episode_count + 1):
            source_slug = f"{slug}-1x{episode_number}"

            try:
                episode = self.animesalt.parse_episode(source_slug)

                if episode.number is not None:
                    season.episodes.append(episode)

            except Exception as exc:
                print(
                    f"Skipping episode {episode_number}: {exc}"
                )

        anime.seasons.append(season)

        return anime
