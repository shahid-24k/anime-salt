from flask import Flask, jsonify, request
from flask_cors import CORS
import requests

from app.service import AnimeService

app = Flask(__name__)

CORS(
    app,
    resources={r"/api/*": {"origins": "*"}}
)

service = AnimeService()


def resolve_source_url(url):
    """
    Resolve redirects from the source URL on the backend.
    Returns the final URL when possible, otherwise the original URL.
    """
    if not url:
        return url

    try:
        response = requests.get(
            url,
            headers={
                "User-Agent": "Mozilla/5.0",
            },
            allow_redirects=True,
            timeout=15,
            stream=True,
        )

        final_url = response.url
        response.close()

        return final_url or url

    except requests.RequestException:
        return url


@app.get("/api/search")
def search():
    query = request.args.get("q", "").strip()

    if not query:
        return jsonify({"error": "Missing q parameter"}), 400

    return jsonify(service.search(query))


@app.get("/api/anime/<query>")
def anime(query):
    result = service.get_anime(query)

    if result is None:
        return jsonify({"error": "Anime not found"}), 404

    seasons = []

    for season in result.seasons:
        episodes = []

        for episode in season.episodes:
            sources = []

            for source in episode.sources:
                resolved_url = resolve_source_url(source.url)

                sources.append({
                    "language": source.language,
                    "url": resolved_url,
                    "server": source.server,
                    "quality": source.quality,
                })

            episodes.append({
                "number": episode.number,
                "title": episode.title,
                "sources": sources,
            })

        seasons.append({
            "number": season.number,
            "episodes": episodes,
        })

    return jsonify({
        "canonical_id": result.canonical_id,
        "title": result.title,
        "alternate_titles": result.alternate_titles,
        "genres": result.genres,
        "image": result.image,
        "popularity": result.popularity,
        "seasons": seasons,
    })


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False,
    )