import { useState } from "react";
import { generateStory } from "../services/api";

export default function StoryForm({ onStoryGenerated }) {
  const [idea, setIdea] = useState("");
  const [genre, setGenre] = useState("aventure");
  const [style, setStyle] = useState("manga");
  const [audience, setAudience] = useState("enfant");
  const [language, setLanguage] = useState("fr");
  const [panelCount, setPanelCount] = useState(4);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const genres = ["aventure", "fantastique", "science-fiction", "comedie", "educatif"];
  const styles = ["manga", "cartoon", "aquarelle", "comics"];
  const audiences = ["enfant", "adolescent", "adulte"];
  const languages = ["fr", "en"];

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const input = {
        idea,
        genre,
        style,
        audience,
        language,
        panel_count: panelCount,
      };
      const story = await generateStory(input);
      onStoryGenerated(story);
    } catch (err) {
      setError(err?.response?.data?.detail || err.message || "Erreur lors de la génération");
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="card">
      <h2>Créer une histoire</h2>
      <form onSubmit={handleSubmit} className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="form-group">
          <label>Idée de l'histoire</label>
          <input
            type="text"
            placeholder="Ex: un robot découvre un jardin à Casablanca"
            value={idea}
            onChange={(e) => setIdea(e.target.value)}
            required
          />
        </div>
        <div className="form-group">
          <label>Genre</label>
          <select value={genre} onChange={(e) => setGenre(e.target.value)}>
            {genres.map((g) => (
              <option key={g} value={g}>
                {g.charAt(0).toUpperCase() + g.slice(1)}
              </option>
            ))}
          </select>
        </div>
        <div className="form-group">
          <label>Style visuel</label>
          <select value={style} onChange={(e) => setStyle(e.target.value)}>
            {styles.map((s) => (
              <option key={s} value={s}>
                {s.charAt(0).toUpperCase() + s.slice(1)}
              </option>
            ))}
          </select>
        </div>
        <div className="form-group">
          <label>Public cible</label>
          <select value={audience} onChange={(e) => setAudience(e.target.value)}>
            {audiences.map((a) => (
              <option key={a} value={a}>{a}</option>
            ))}
          </select>
        </div>
        <div className="form-group">
          <label>Langue</label>
          <select value={language} onChange={(e) => setLanguage(e.target.value)}>
            {languages.map((l) => (
              <option key={l} value={l}>{l.toUpperCase()}</option>
            ))}
          </select>
        </div>
        <div className="form-group">
          <label>Nombre de cases</label>
          <input
            type="number"
            min={1}
            max={12}
            value={panelCount}
            onChange={(e) => setPanelCount(Math.max(1, Math.min(12, Number(e.target.value))))}
          />
        </div>
        <div className="form-group col-span-full">
          <button type="submit" disabled={loading} className="btn">
            {loading ? "Génération en cours…" : "Générer l'histoire"}
          </button>
        </div>
        {error && <div className="error" role="alert">{error}</div>}
      </form>
    </section>
  );
}
