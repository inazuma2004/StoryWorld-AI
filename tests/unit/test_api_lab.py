"""Tests de l'API du laboratoire VAE / DCGAN."""

import torch
from torch.utils.data import DataLoader, TensorDataset


def _synthetic_loader(*_args, **_kwargs):
    images = torch.rand(4, 1, 28, 28)
    labels = torch.zeros(4, dtype=torch.long)
    return DataLoader(TensorDataset(images, labels), batch_size=4)


def test_lab_status(client):
    response = client.get("/api/v1/lab/status")

    assert response.status_code == 200
    data = response.json()
    assert "vae" in data
    assert "dcgan" in data


def test_lab_train_vae_avec_donnees_synthetiques(client, tmp_path, monkeypatch):
    from storyworld.api import main
    from storyworld.config import Settings

    monkeypatch.setattr(main, "get_settings", lambda: Settings(data_dir=tmp_path))
    monkeypatch.setattr(main, "make_fashion_mnist_loader", _synthetic_loader)

    response = client.post(
        "/api/v1/lab/train/vae",
        json={"epochs": 1, "limit_batches": 1, "batch_size": 4, "latent_dim": 4},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["model"] == "vae"
    assert len(data["history"]["loss"]) == 1
    assert data["samples"]["reconstructions"].startswith("/lab-media/")


def test_lab_train_dcgan_avec_donnees_synthetiques(client, tmp_path, monkeypatch):
    from storyworld.api import main
    from storyworld.config import Settings

    monkeypatch.setattr(main, "get_settings", lambda: Settings(data_dir=tmp_path))
    monkeypatch.setattr(main, "make_fashion_mnist_loader", _synthetic_loader)

    response = client.post(
        "/api/v1/lab/train/dcgan",
        json={"epochs": 1, "limit_batches": 1, "batch_size": 4, "latent_dim": 4},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["model"] == "dcgan"
    assert len(data["history"]["d_loss"]) == 1
    assert data["samples"]["samples"].startswith("/lab-media/")


def test_lab_train_modele_inconnu_422(client):
    response = client.post("/api/v1/lab/train/inconnu", json={})
    assert response.status_code == 422
