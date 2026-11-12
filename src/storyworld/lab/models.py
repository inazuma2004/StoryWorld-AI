"""Modèles du laboratoire : VAE et DCGAN pour Fashion-MNIST (28×28)."""

from __future__ import annotations

import torch
from torch import nn
from torch.nn import functional as F


class VAE(nn.Module):
    """Autoencodeur variationnel convolutif pour images 1×28×28."""

    def __init__(self, latent_dim: int = 16):
        super().__init__()
        self.latent_dim = latent_dim

        self.encoder = nn.Sequential(
            nn.Conv2d(1, 16, kernel_size=4, stride=2, padding=1),  # 14×14
            nn.ReLU(inplace=True),
            nn.Conv2d(16, 32, kernel_size=4, stride=2, padding=1),  # 7×7
            nn.ReLU(inplace=True),
            nn.Flatten(),
        )
        self.fc_mu = nn.Linear(32 * 7 * 7, latent_dim)
        self.fc_logvar = nn.Linear(32 * 7 * 7, latent_dim)

        self.decoder_input = nn.Linear(latent_dim, 32 * 7 * 7)
        self.decoder = nn.Sequential(
            nn.Unflatten(1, (32, 7, 7)),
            nn.ConvTranspose2d(32, 16, kernel_size=4, stride=2, padding=1),  # 14×14
            nn.ReLU(inplace=True),
            nn.ConvTranspose2d(16, 1, kernel_size=4, stride=2, padding=1),  # 28×28
            nn.Sigmoid(),
        )

    def encode(self, images: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        hidden = self.encoder(images)
        return self.fc_mu(hidden), self.fc_logvar(hidden)

    def reparameterize(self, mu: torch.Tensor, logvar: torch.Tensor) -> torch.Tensor:
        std = torch.exp(0.5 * logvar)
        epsilon = torch.randn_like(std)
        return mu + epsilon * std

    def decode(self, z: torch.Tensor) -> torch.Tensor:
        hidden = self.decoder_input(z)
        return self.decoder(hidden)

    def forward(
        self, images: torch.Tensor
    ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        mu, logvar = self.encode(images)
        z = self.reparameterize(mu, logvar)
        return self.decode(z), mu, logvar


def vae_loss(
    reconstruction: torch.Tensor,
    target: torch.Tensor,
    mu: torch.Tensor,
    logvar: torch.Tensor,
) -> torch.Tensor:
    """Perte VAE : reconstruction BCE + divergence KL, moyennées par image."""
    reconstruction_loss = F.binary_cross_entropy(
        reconstruction, target, reduction="sum"
    ) / target.size(0)
    kl_loss = -0.5 * torch.sum(1 + logvar - mu.pow(2) - logvar.exp()) / target.size(0)
    return reconstruction_loss + kl_loss


@torch.no_grad()
def interpolate(
    model: VAE, z1: torch.Tensor, z2: torch.Tensor, steps: int = 8
) -> torch.Tensor:
    """Décode une interpolation linéaire entre deux vecteurs latents."""
    model.eval()
    frames = []
    for alpha in torch.linspace(0.0, 1.0, steps):
        z = z1 * (1 - alpha) + z2 * alpha
        frames.append(model.decode(z.unsqueeze(0)).squeeze(0))
    return torch.clamp(torch.stack(frames), 0.0, 1.0)


class DCGANGenerator(nn.Module):
    """Générateur DCGAN produisant des images 1×28×28 dans [-1, 1]."""

    def __init__(self, latent_dim: int = 32):
        super().__init__()
        self.latent_dim = latent_dim
        self.net = nn.Sequential(
            nn.Linear(latent_dim, 32 * 7 * 7),
            nn.ReLU(inplace=True),
            nn.Unflatten(1, (32, 7, 7)),
            nn.ConvTranspose2d(32, 16, kernel_size=4, stride=2, padding=1),  # 14×14
            nn.ReLU(inplace=True),
            nn.ConvTranspose2d(16, 1, kernel_size=4, stride=2, padding=1),  # 28×28
            nn.Tanh(),
        )

    def forward(self, z: torch.Tensor) -> torch.Tensor:
        return self.net(z)


class DCGANDiscriminator(nn.Module):
    """Discriminateur DCGAN renvoyant une probabilité par image."""

    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Conv2d(1, 16, kernel_size=4, stride=2, padding=1),  # 14×14
            nn.LeakyReLU(0.2, inplace=True),
            nn.Conv2d(16, 32, kernel_size=4, stride=2, padding=1),  # 7×7
            nn.LeakyReLU(0.2, inplace=True),
            nn.Flatten(),
            nn.Linear(32 * 7 * 7, 1),
            nn.Sigmoid(),
        )

    def forward(self, images: torch.Tensor) -> torch.Tensor:
        return self.net(images)
