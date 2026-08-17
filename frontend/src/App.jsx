import { useState } from "react";
import { Search, Play, Loader2 } from "lucide-react";
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
        `${API}/api/search?q=${encodeURIComponent(query)}`
      );
      const data = await response.json();
      setResults(data);
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

  const episodes = anime?.seasons?.[0]?.episodes || [];

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
                <button type="submit">
                  {loading ? <Loader2 className="spin" /> : "Search"}
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

        {!anime && results.length > 0 && (
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
                    <h3>{item.title?.english || item.title?.romaji}</h3>
                    <p>{item.genres?.slice(0, 3).join(" • ")}</p>
                    <span>{item.episodes || "?"} episodes</span>
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
                <p className="genres">{anime.genres?.join(" • ")}</p>
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
                      onClick={() => {
                        setSelectedEpisode(episode);
                        setSelectedLanguage(null);
                      }}
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
                    <p>Choose an episode to see its available languages.</p>
                  </div>
                ) : (
                  <>
                    <div className="player-placeholder">
                      <Play size={48} />
                      <h3>Episode {selectedEpisode.number}</h3>
                      <p>Select a language below.</p>
                    </div>

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

                    {selectedLanguage && (
                      <p className="selected">
                        Selected language: <strong>{selectedLanguage}</strong>
                      </p>
                    )}
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
