import { mediaUrl } from "../services/api";

export default function StoryViewer({ story }) {
  if (!story) return null;

  return (
    <section className="card" aria-label="Histoire générée">
      <h2>{story.title}</h2>
      <p className="synopsis">{story.synopsis}</p>

      <h3>Personnages</h3>
      <ul className="list">
        {(story.characters || []).map((c, i) => (
          <li key={`${c.name}-${i}`}>
            <strong>{c.name}</strong> — {c.role} ({c.personnalite})
          </li>
        ))}
      </ul>

      <h3>Scènes et cases</h3>
      {(story.scenes || []).map((scene) => (
        <div key={scene.numero} className="scene">
          <h4>
            Scène {scene.numero} : {scene.description}
          </h4>
          <div className="panels">
            {(scene.panels || []).map((panel) => (
              <Panel key={panel.numero} panel={panel} />
            ))}
          </div>
        </div>
      ))}
    </section>
  );
}

function Panel({ panel }) {
  const url = mediaUrl(panel.image_url);
  const failed = panel.status === "error";

  return (
    <figure className="panel">
      <div className="panel-image">
        {url && !failed ? (
          <img
            src={url}
            alt={`Illustration de la case ${panel.numero} : ${panel.description_visuelle}`}
            loading="lazy"
          />
        ) : (
          <div className="panel-placeholder" role="img" aria-label="Illustration indisponible">
            Illustration indisponible
          </div>
        )}
      </div>
      <figcaption>
        <p className="dialogue">{panel.dialogue}</p>
        <p className="panel-desc">{panel.description_visuelle}</p>
        <p className="characters">
          Personnages : {(panel.personnages || []).join(", ")}
        </p>
      </figcaption>
    </figure>
  );
}
