from flask import Flask, jsonify, request
from flask_cors import CORS

from app.service import AnimeService


app = Flask(__name__)

CORS(
    app,
    resources={
        r"/api/*": {
            "origins": "*"
        }
    }
)

service = AnimeService()


@app.get("/")
def root():
    return jsonify({
        "name": "Anime VLC API",
        "status": "online",
        "version": "1.0.0"
    })


@app.get("/health")
def health():
    return jsonify({
        "status": "ok"
    })


@app.get("/api/search")
def search():
    query = request.args.get("q", "").strip()

    if not query:
        return jsonify({
            "error": "Missing q parameter"
        }), 400

    try:
        results = service.search(query)
        return jsonify(results)

    except Exception as exc:
        app.logger.exception("Search failed")

        return jsonify({
            "error": "Search failed",
            "message": str(exc)
        }), 502


@app.get("/api/anime/<path:query>")
def anime(query):
    query = query.strip()

    if not query:
        return jsonify({
            "error": "Missing anime query"
        }), 400

    try:
        result = service.get_anime(query)

        if result is None:
            return jsonify({
                "error": "Anime not found"
            }), 404

        seasons = []

        for season in result.seasons:
            episodes = []

            for episode in season.episodes:
                sources = []

                for source in episode.sources:
                    if not source.url:
                        continue

                    sources.append({
                        "language": source.language,
                        "url": source.url,
                        "server": source.server,
                        "quality": source.quality
                    })

                episodes.append({
                    "number": episode.number,
                    "title": episode.title,
                    "sources": sources,
                    "provider_ids": episode.provider_ids
                })

            seasons.append({
                "number": season.number,
                "episodes": episodes
            })

        return jsonify({
            "canonical_id": result.canonical_id,
            "title": result.title,
            "alternate_titles": result.alternate_titles,
            "genres": result.genres,
            "image": result.image,
            "popularity": result.popularity,
            "seasons": seasons
        })

    except Exception as exc:
        app.logger.exception("Anime lookup failed")

        return jsonify({
            "error": "Anime lookup failed",
            "message": str(exc)
        }), 502


@app.errorhandler(404)
def not_found(_error):
    return jsonify({
        "error": "Not found"
    }), 404


@app.errorhandler(500)
def internal_error(_error):
    return jsonify({
        "error": "Internal server error"
    }), 500


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )
