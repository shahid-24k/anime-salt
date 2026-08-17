import requests


class AniListProvider:
    API_URL = "https://graphql.anilist.co"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "User-Agent": "Anime-VLC/1.0"
        })

    def search(self, query):
        graphql = """
        query ($search: String) {
            Page(perPage: 10) {
                media(search: $search, type: ANIME) {
                    id
                    title {
                        romaji
                        english
                        native
                    }
                    coverImage {
                        large
                    }
                    genres
                    popularity
                    averageScore
                    episodes
                    status
                }
            }
        }
        """

        response = self.session.post(
            self.API_URL,
            json={
                "query": graphql,
                "variables": {"search": query}
            },
            timeout=20
        )

        response.raise_for_status()

        data = response.json()

        if "errors" in data:
            raise RuntimeError(data["errors"])

        return data["data"]["Page"]["media"]
