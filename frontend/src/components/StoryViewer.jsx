export default function StoryViewer({ story }) {
  if (!story) return null;

  return (
    <section className="card">
      <h2>{story.title}</h2>
      <p>{story.synopsis}</p>

      <h3>Personnages</h3>
      <ul className="list">
        {(story.characters || []).map((c, i) => (
          <li key={i}>
            <strong>{c.name}</strong> — {c.role} ({c.personnalite})
          </li>
        ))}
      </ul>

      <h3>Scènes et cases</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {(story.scenes || []).map((scene) => (
          <div key={scene.numero} className="scene">
            <h4>Scène {scene.numero}: {scene.description}</h4>
            <div className="panels">
              {(scene.panels || []).map((panel) => (
                <div key={panel.numero} className="panel">
                  <div className="panel-placeholder" />
                  <p className="dialogue">{panel.dialogue}</p>
                  <p className="panel-desc">{panel.description_visuelle}</p>
                  <p className="characters">
                    Personnages: {(panel.personnages || []).join(", ")}
                  </p>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
