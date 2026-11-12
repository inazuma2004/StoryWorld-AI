import { useCallback, useEffect, useState } from "react";
import { getLabStatus, mediaUrl, trainLabModel } from "../services/api";

const DEMO_OPTIONS = {
  epochs: 1,
  limit_batches: 10,
  batch_size: 32,
  latent_dim: 16,
};

export default function LabPanel() {
  const [status, setStatus] = useState(null);
  const [loadingModel, setLoadingModel] = useState(null);
  const [error, setError] = useState(null);
  const [cacheKey, setCacheKey] = useState(() => Date.now());

  const refresh = useCallback(async () => {
    try {
      setStatus(await getLabStatus());
    } catch (err) {
      setError(err.message);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const handleTrain = async (model) => {
    setError(null);
    setLoadingModel(model);
    try {
      await trainLabModel(model, DEMO_OPTIONS);
      setCacheKey(Date.now());
      await refresh();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoadingModel(null);
    }
  };

  return (
    <section className="card" aria-label="Laboratoire IA">
      <h2>Laboratoire IA : VAE et DCGAN</h2>
      <p className="synopsis">
        Deux modèles entraînés localement sur Fashion-MNIST (images 28×28) pour
        comparer reconstruction et génération adversariale. Ces modèles sont
        expérimentaux : ils ne produisent pas les illustrations de la BD.
      </p>

      {error && (
        <div className="error" role="alert">
          {error}
        </div>
      )}

      <div className="lab-grid">
        <article className="lab-card">
          <h3>VAE — reconstruction et espace latent</h3>
          <p className="panel-desc">
            En haut : images originales. En bas : reconstructions par le VAE.
            L'interpolation montre un trajet continu entre deux vecteurs latents.
          </p>
          <LabImages
            available={status?.vae?.available}
            images={[
              ["Reconstructions", status?.vae?.samples?.reconstructions],
              ["Interpolation latente", status?.vae?.samples?.interpolation],
            ]}
            cacheKey={cacheKey}
          />
          <Metrics history={status?.vae?.history} keys={["loss", "reconstruction", "kl"]} />
          <button
            type="button"
            className="btn"
            onClick={() => handleTrain("vae")}
            disabled={loadingModel !== null}
          >
            {loadingModel === "vae" ? "Entraînement VAE…" : "Entraîner le VAE (démo)"}
          </button>
        </article>

        <article className="lab-card">
          <h3>DCGAN — génération adversariale</h3>
          <p className="panel-desc">
            Échantillons produits par le générateur après quelques lots
            d'entraînement. Les formes se précisent avec les epochs ; un
            entraînement court reste bruité (mode collapse possible).
          </p>
          <LabImages
            available={status?.dcgan?.available}
            images={[["Échantillons générés", status?.dcgan?.samples?.samples]]}
            cacheKey={cacheKey}
          />
          <Metrics history={status?.dcgan?.history} keys={["d_loss", "g_loss"]} />
          <button
            type="button"
            className="btn"
            onClick={() => handleTrain("dcgan")}
            disabled={loadingModel !== null}
          >
            {loadingModel === "dcgan" ? "Entraînement DCGAN…" : "Entraîner le DCGAN (démo)"}
          </button>
        </article>
      </div>

      <p className="notice">
        Démo : 1 epoch sur 10 lots (CPU). Pour un résultat de qualité, lancer
        l'entraînement complet en ligne de commande :
        <code>python -m storyworld.lab.train --model vae --epochs 10</code>
      </p>
    </section>
  );
}

function LabImages({ available, images, cacheKey }) {
  if (!available) {
    return (
      <div className="panel-placeholder lab-placeholder">
        Aucun artefact disponible : lancez une démo.
      </div>
    );
  }
  return (
    <div className="lab-images">
      {images.map(([label, url]) =>
        url ? (
          <figure key={label}>
            <img
              src={`${mediaUrl(url)}?v=${cacheKey}`}
              alt={label}
              loading="lazy"
            />
            <figcaption>{label}</figcaption>
          </figure>
        ) : null
      )}
    </div>
  );
}

function Metrics({ history, keys }) {
  if (!history) return null;
  const lastValues = keys
    .filter((key) => Array.isArray(history[key]) && history[key].length > 0)
    .map((key) => `${key} : ${history[key][history[key].length - 1].toFixed(2)}`);

  if (lastValues.length === 0) return null;
  return <p className="lab-metrics">Dernières pertes — {lastValues.join(" · ")}</p>;
}
