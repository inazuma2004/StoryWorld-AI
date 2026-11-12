import { useState } from "react";
import { generateStory } from "../services/api";

const GENRES = ["aventure", "fantastique", "science-fiction", "comedie", "educatif"];
const STYLES = ["manga", "cartoon", "aquarelle", "comics"];
const AUDIENCES = ["enfant", "adolescent", "adulte"];
const LANGUAGES = ["fr", "en"];

export default function StoryForm({ onStoryGenerated }) {
  const [idea, setIdea] = useState("");
  const [genre, setGenre] = useState("aventure");
  const [style, setStyle] = useState("manga");
  const [audience, setAudience] = useState("enfant");
  const [language, setLanguage] = useState("fr");
  const [panelCount, setPanelCount] = useState(4);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const story = await generateStory({
        idea,
        genre,
        style,
        audience,
        language,
        panel_count: panelCount,
      });
      onStoryGenerated(story);
    } catch (err) {
      setError(err.message || "Erreur lors de la génération");
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="card">
      <h2>Créer une histoire</h2>
      <form onSubmit={handleSubmit} className="form-grid">
        <div className="form-group">
          <label htmlFor="idea">Idée de l'histoire</label>
          <input
            id="idea"
            type="text"
            placeholder="Ex: un robot découvre un jardin à Casablanca"
            value={idea}
            onChange={(e) => setIdea(e.target.value)}
            required
          />
        </div>
        <div className="form-group">
          <label htmlFor="genre">Genre</label>
          <select id="genre" value={genre} onChange={(e) => setGenre(e.target.value)}>
            {GENRES.map((g) => (
              <option key={g} value={g}>
                {g.charAt(0).toUpperCase() + g.slice(1)}
              </option>
            ))}
          </select>
        </div>
        <div className="form-group">
          <label htmlFor="style">Style visuel</label>
          <select id="style" value={style} onChange={(e) => setStyle(e.target.value)}>
            {STYLES.map((s) => (
              <option key={s} value={s}>
                {s.charAt(0).toUpperCase() + s.slice(1)}
              </option>
            ))}
          </select>
        </div>
        <div className="form-group">
          <label htmlFor="audience">Public cible</label>
          <select id="audience" value={audience} onChange={(e) => setAudience(e.target.value)}>
            {AUDIENCES.map((a) => (
              <option key={a} value={a}>{a}</option>
            ))}
          </select>
        </div>
        <div className="form-group">
          <label htmlFor="language">Langue</label>
          <select id="language" value={language} onChange={(e) => setLanguage(e.target.value)}>
            {LANGUAGES.map((l) => (
              <option key={l} value={l}>{l.toUpperCase()}</option>
            ))}
          </select>
        </div>
        <div className="form-group">
          <label htmlFor="panel-count">Nombre de cases</label>
          <input
            id="panel-count"
            type="number"
            min={1}
            max={12}
            value={panelCount}
            onChange={(e) => setPanelCount(Math.max(1, Math.min(12, Number(e.target.value))))}
          />
        </div>
        <div className="form-actions">
          <button type="submit" disabled={loading} className="btn">
            {loading ? "Génération en cours…" : "Générer l'histoire"}
          </button>
        </div>
        {error && (
          <div className="error" role="alert" aria-live="assertive">
            {error}
          </div>
        )}
      </form>
    </section>
  );
}
