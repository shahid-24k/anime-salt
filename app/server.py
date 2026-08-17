from flask import Flask, jsonify

from app.service import AnimeService

app = Flask(__name__)
service = AnimeService()


@app.get("/api/search")
def search():
    from flask import request

    query = request.args.get("q", "").strip()

    if not query:
        return jsonify({"error": "Missing q parameter"}), 400

    return jsonify(service.search(query))


@app.get("/api/anime/<query>")
def anime(query):
    result = service.get_anime(query)

    if result is None:
        return jsonify({"error": "Anime not found"}), 404

    return jsonify({
        "canonical_id": result.canonical_id,
        "title": result.title,
        "alternate_titles": result.alternate_titles,
        "genres": result.genres,
        "image": result.image,
        "popularity": result.popularity,
        "seasons": [
            {
                "number": season.number,
                "episodes": [
                    {
                        "number": episode.number,
                        "title": episode.title,
                        "sources": [
                            {
                                "language": source.language,
                                "url": source.url,
                                "server": source.server,
                                "quality": source.quality
                            }
                            for source in episode.sources
                        ]
                    }
                    for episode in season.episodes
                ]
            }
            for season in result.seasons
        ]
    })


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
