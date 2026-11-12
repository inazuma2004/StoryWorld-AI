"""Tests du pipeline d'entraînement du laboratoire (données synthétiques)."""

import json
import math

import torch
from torch.utils.data import DataLoader, TensorDataset

from storyworld.lab.models import VAE, DCGANDiscriminator, DCGANGenerator
from storyworld.lab.train import (
    resolve_device,
    save_image_grid,
    train_dcgan,
    train_vae,
)


def _loader(batches: int = 2, batch_size: int = 4) -> DataLoader:
    images = torch.rand(batches * batch_size, 1, 28, 28)
    labels = torch.zeros(batches * batch_size, dtype=torch.long)
    return DataLoader(TensorDataset(images, labels), batch_size=batch_size)


def test_resolve_device_retourne_cpu_ou_cuda():
    assert resolve_device("auto") in ("cpu", "cuda")
    assert resolve_device("cpu") == "cpu"


def test_train_vae_historique_et_checkpoint(tmp_path):
    model = VAE(latent_dim=4)

    history = train_vae(
        model,
        _loader(),
        epochs=1,
        device="cpu",
        limit_batches=2,
        checkpoint_path=tmp_path / "vae.pt",
    )

    assert len(history["loss"]) == 2
    assert all(math.isfinite(value) and value >= 0 for value in history["loss"])
    assert (tmp_path / "vae.pt").exists()


def test_train_dcgan_historique_et_checkpoint(tmp_path):
    generator = DCGANGenerator(latent_dim=8)
    discriminator = DCGANDiscriminator()

    history = train_dcgan(
        generator,
        discriminator,
        _loader(),
        epochs=1,
        device="cpu",
        limit_batches=2,
        checkpoint_path=tmp_path / "dcgan.pt",
    )

    assert len(history["d_loss"]) == 2
    assert len(history["g_loss"]) == 2
    assert all(
        math.isfinite(value) for value in history["d_loss"] + history["g_loss"]
    )
    assert (tmp_path / "dcgan.pt").exists()


def test_save_image_grid(tmp_path):
    output = tmp_path / "grid.png"

    save_image_grid(torch.rand(8, 1, 28, 28), output)

    assert output.exists()
    assert output.stat().st_size > 0


def test_checkpoint_contient_les_poids(tmp_path):
    model = VAE(latent_dim=4)
    path = tmp_path / "vae.pt"

    train_vae(model, _loader(), epochs=1, device="cpu", limit_batches=1, checkpoint_path=path)

    payload = torch.load(path, map_location="cpu", weights_only=True)
    assert "state_dict" in payload
    assert "latent_dim" in payload
    assert json.dumps(payload["latent_dim"]) is not None
