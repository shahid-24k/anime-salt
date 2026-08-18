import { useState } from "react";
import { ExternalLink, Loader2, Play, Search } from "lucide-react";
import "./App.css";

const API = "https://anime-salt-api.onrender.com";

export default function App() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [anime, setAnime] = useState(null);
  const [loading, setLoading] = useState(false);
  const [selectedEpisode, setSelectedEpisode] = useState(null);
  const [selectedLanguage, setSelectedLanguage] = useState(null);

  async function searchAnime(e) {
    e?.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setAnime(null);

    try {
      const response = await fetch(
        `${API}/api/search?q=${encodeURIComponent(query.trim())}`
      );
      if (!response.ok) throw new Error();
      const data = await response.json();
      setResults(Array.isArray(data) ? data : []);
    } catch {
      setResults([]);
    } finally {
      setLoading(false);
    }
  }

  async function openAnime(item) {
    setLoading(true);

    try {
      const title = item.title?.english || item.title?.romaji || query;
      const response = await fetch(
        `${API}/api/anime/${encodeURIComponent(title)}`
      );

      if (!response.ok) throw new Error();

      const data = await response.json();

      setAnime(data);
      setResults([]);
      setSelectedEpisode(null);
      setSelectedLanguage(null);
    } catch {
      setAnime(null);
    } finally {
      setLoading(false);
    }
  }

  function selectEpisode(episode) {
    setSelectedEpisode(episode);
    setSelectedLanguage(episode.sources?.[0]?.language || null);
  }

  const episodes = anime?.seasons?.[0]?.episodes || [];

  const selectedSource = selectedEpisode?.sources?.find(
    (source) => source.language === selectedLanguage
  );

  return (
    <div className="app">
      <header className="navbar">
        <div className="brand">
          <div className="brand-mark">A</div>
          <span>Anime VLC</span>
        </div>

        <form className="search" onSubmit={searchAnime}>
          <Search size={19} />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search anime..."
          />
        </form>
      </header>

      <main>
        {!anime && (
          <section className="hero">
            <div>
              <p className="eyebrow">YOUR ANIME HUB</p>
              <h1>Watch. Discover.<br />Enjoy.</h1>

              <p className="hero-text">
                Search your favorite anime and explore available episodes,
                languages and metadata.
              </p>

              <form className="hero-search" onSubmit={searchAnime}>
                <Search size={21} />

                <input
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Search Death Note..."
                />

                <button type="submit" disabled={loading}>
                  {loading ? (
                    <Loader2 className="spin" size={20} />
                  ) : (
                    "Search"
                  )}
                </button>
              </form>
            </div>
          </section>
        )}

        {loading && (
          <div className="loading">
            <Loader2 className="spin" />
            <span>Loading...</span>
          </div>
        )}

        {!anime && !loading && results.length > 0 && (
          <section className="results">
            <h2>Search results</h2>

            <div className="cards">
              {results.map((item) => (
                <button
                  className="anime-card"
                  key={item.id}
                  onClick={() => openAnime(item)}
                >
                  <img
                    src={item.coverImage?.large}
                    alt={item.title?.english || item.title?.romaji}
                  />

                  <div className="card-info">
                    <h3>
                      {item.title?.english || item.title?.romaji}
                    </h3>

                    <p>
                      {item.genres?.slice(0, 3).join(" • ")}
                    </p>

                    <span>
                      {item.episodes || "?"} episodes
                    </span>
                  </div>
                </button>
              ))}
            </div>
          </section>
        )}

        {anime && (
          <section className="anime-page">
            <button
              className="back"
              onClick={() => {
                setAnime(null);
                setSelectedEpisode(null);
                setSelectedLanguage(null);
              }}
            >
              ← Back to search
            </button>

            <div className="anime-header">
              <img src={anime.image} alt={anime.title} />

              <div>
                <p className="eyebrow">ANIME</p>

                <h1>{anime.title}</h1>

                <p className="genres">
                  {anime.genres?.join(" • ")}
                </p>

                <p className="popularity">
                  Popularity #{anime.popularity?.toLocaleString()}
                </p>
              </div>
            </div>

            <div className="content-grid">
              <div>
                <h2>Episodes</h2>

                <div className="episodes">
                  {episodes.map((episode) => (
                    <button
                      key={episode.number}
                      className={
                        selectedEpisode?.number === episode.number
                          ? "episode active"
                          : "episode"
                      }
                      onClick={() => selectEpisode(episode)}
                    >
                      {episode.number}
                    </button>
                  ))}
                </div>
              </div>

              <div className="player-panel">
                {!selectedEpisode ? (
                  <div className="empty-player">
                    <Play size={42} />
                    <h3>Select an episode</h3>
                    <p>
                      Choose an episode to start playback.
                    </p>
                  </div>
                ) : (
                  <>
                    <div className="player-topbar">
                      <div>
                        <strong>{anime.title}</strong>
                        <span>
                          Episode {selectedEpisode.number}
                        </span>
                      </div>

                      {selectedSource?.url && (
                        <a
                          className="source-link"
                          href={selectedSource.url}
                          target="_blank"
                          rel="noreferrer"
                          title="Open source"
                        >
                          <ExternalLink size={16} />
                        </a>
                      )}
                    </div>

                    {selectedSource?.url ? (
                      <div className="video-frame">
                        <iframe
                          key={selectedSource.url}
                          src={selectedSource.url}
                          title={`${anime.title} Episode ${selectedEpisode.number}`}
                          allow="autoplay; fullscreen; picture-in-picture"
                          allowFullScreen
                          referrerPolicy="no-referrer"
                        />
                      </div>
                    ) : (
                      <div className="empty-player compact">
                        <p>
                          No playable source is available.
                        </p>
                      </div>
                    )}

                    <div className="player-footer">
                      <div className="languages">
                        {selectedEpisode.sources?.map((source) => (
                          <button
                            key={source.language}
                            className={
                              selectedLanguage === source.language
                                ? "language active"
                                : "language"
                            }
                            onClick={() =>
                              setSelectedLanguage(source.language)
                            }
                          >
                            {source.language}
                          </button>
                        ))}
                      </div>

                      <span className="selected">
                        {selectedLanguage || "No language selected"}
                      </span>
                    </div>
                  </>
                )}
              </div>
            </div>
          </section>
        )}
      </main>
    </div>
  );
}
