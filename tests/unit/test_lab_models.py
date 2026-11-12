"""Tests des modèles du laboratoire VAE / DCGAN."""

import torch

from storyworld.lab.models import (
    VAE,
    DCGANDiscriminator,
    DCGANGenerator,
    interpolate,
    vae_loss,
)


def test_vae_forward_shapes():
    model = VAE(latent_dim=8)
    images = torch.rand(4, 1, 28, 28)

    reconstruction, mu, logvar = model(images)

    assert reconstruction.shape == (4, 1, 28, 28)
    assert mu.shape == (4, 8)
    assert logvar.shape == (4, 8)
    assert reconstruction.min() >= 0
    assert reconstruction.max() <= 1


def test_vae_loss_est_finie_et_positive():
    model = VAE(latent_dim=8)
    images = torch.rand(4, 1, 28, 28)
    reconstruction, mu, logvar = model(images)

    loss = vae_loss(reconstruction, images, mu, logvar)

    assert torch.isfinite(loss)
    assert loss.item() > 0


def test_vae_interpolation_shapes_et_bornes():
    model = VAE(latent_dim=8)
    z1 = torch.randn(8)
    z2 = torch.randn(8)

    frames = interpolate(model, z1, z2, steps=5)

    assert frames.shape == (5, 1, 28, 28)
    assert frames.min() >= 0
    assert frames.max() <= 1


def test_dcgan_generator_shapes():
    generator = DCGANGenerator(latent_dim=16)

    images = generator(torch.randn(4, 16))

    assert images.shape == (4, 1, 28, 28)
    assert images.min() >= -1
    assert images.max() <= 1


def test_dcgan_discriminator_shapes():
    discriminator = DCGANDiscriminator()

    scores = discriminator(torch.rand(4, 1, 28, 28))

    assert scores.shape == (4, 1)
    assert scores.min() >= 0
    assert scores.max() <= 1
