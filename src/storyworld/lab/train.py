"""Entraînement VAE / DCGAN sur Fashion-MNIST (CPU ou GPU)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import torch
from torch import nn
from torch.nn import functional as F
from torch.utils.data import DataLoader
from torchvision import datasets, transforms
from torchvision.utils import save_image

from storyworld.lab.models import (
    VAE,
    DCGANDiscriminator,
    DCGANGenerator,
    interpolate,
)


def resolve_device(device: str = "auto") -> str:
    if device == "auto":
        return "cuda" if torch.cuda.is_available() else "cpu"
    return device


def make_fashion_mnist_loader(
    data_dir: Path,
    batch_size: int = 64,
    *,
    train: bool = True,
    download: bool = True,
) -> DataLoader:
    transform = transforms.Compose([transforms.ToTensor()])
    dataset = datasets.FashionMNIST(
        root=str(data_dir),
        train=train,
        download=download,
        transform=transform,
    )
    return DataLoader(dataset, batch_size=batch_size, shuffle=train)


def train_vae(
    model: VAE,
    dataloader: DataLoader,
    *,
    epochs: int = 1,
    lr: float = 1e-3,
    device: str = "cpu",
    limit_batches: int | None = None,
    seed: int = 42,
    checkpoint_path: Path | None = None,
) -> dict[str, list[float]]:
    """Entraîne un VAE et renvoie l'historique des pertes."""
    torch.manual_seed(seed)
    model.to(device)
    model.train()
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    history: dict[str, list[float]] = {"loss": [], "reconstruction": [], "kl": []}

    for _epoch in range(epochs):
        for batch_index, (images, _labels) in enumerate(dataloader):
            images = images.to(device)
            reconstruction, mu, logvar = model(images)

            reconstruction_loss = F.binary_cross_entropy(
                reconstruction, images, reduction="sum"
            ) / images.size(0)
            kl_loss = -0.5 * torch.sum(
                1 + logvar - mu.pow(2) - logvar.exp()
            ) / images.size(0)
            loss = reconstruction_loss + kl_loss

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            history["loss"].append(float(loss.item()))
            history["reconstruction"].append(float(reconstruction_loss.item()))
            history["kl"].append(float(kl_loss.item()))

            if limit_batches is not None and batch_index + 1 >= limit_batches:
                break

    if checkpoint_path is not None:
        checkpoint_path = Path(checkpoint_path)
        checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
        torch.save(
            {
                "state_dict": model.state_dict(),
                "latent_dim": model.latent_dim,
                "history": history,
            },
            checkpoint_path,
        )
    return history


def train_dcgan(
    generator: DCGANGenerator,
    discriminator: DCGANDiscriminator,
    dataloader: DataLoader,
    *,
    epochs: int = 1,
    lr: float = 2e-4,
    device: str = "cpu",
    limit_batches: int | None = None,
    seed: int = 42,
    checkpoint_path: Path | None = None,
) -> dict[str, list[float]]:
    """Entraîne un DCGAN et renvoie les pertes du générateur et du discriminateur."""
    torch.manual_seed(seed)
    generator.to(device)
    discriminator.to(device)
    generator.train()
    discriminator.train()

    criterion = nn.BCELoss()
    optimizer_g = torch.optim.Adam(generator.parameters(), lr=lr, betas=(0.5, 0.999))
    optimizer_d = torch.optim.Adam(
        discriminator.parameters(), lr=lr, betas=(0.5, 0.999)
    )
    latent_dim = generator.latent_dim
    history: dict[str, list[float]] = {"d_loss": [], "g_loss": []}

    for _epoch in range(epochs):
        for batch_index, (images, _labels) in enumerate(dataloader):
            real_images = images.to(device) * 2 - 1
            batch_size = real_images.size(0)

            optimizer_d.zero_grad()
            real_scores = discriminator(real_images)
            real_loss = criterion(real_scores, torch.ones_like(real_scores))

            noise = torch.randn(batch_size, latent_dim, device=device)
            fake_images = generator(noise)
            fake_scores = discriminator(fake_images.detach())
            fake_loss = criterion(fake_scores, torch.zeros_like(fake_scores))

            d_loss = real_loss + fake_loss
            d_loss.backward()
            optimizer_d.step()

            optimizer_g.zero_grad()
            generated = generator(torch.randn(batch_size, latent_dim, device=device))
            generated_scores = discriminator(generated)
            g_loss = criterion(generated_scores, torch.ones_like(generated_scores))
            g_loss.backward()
            optimizer_g.step()

            history["d_loss"].append(float(d_loss.item()))
            history["g_loss"].append(float(g_loss.item()))

            if limit_batches is not None and batch_index + 1 >= limit_batches:
                break

    if checkpoint_path is not None:
        checkpoint_path = Path(checkpoint_path)
        checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
        torch.save(
            {
                "generator": generator.state_dict(),
                "discriminator": discriminator.state_dict(),
                "latent_dim": latent_dim,
                "history": history,
            },
            checkpoint_path,
        )
    return history


@torch.no_grad()
def save_image_grid(images: torch.Tensor, path: Path, nrow: int = 8) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    save_image(images.cpu(), str(path), nrow=nrow, padding=2)
    return path


def save_vae_samples(
    model: VAE, dataloader: DataLoader, output_dir: Path, device: str = "cpu"
) -> dict[str, Path]:
    """Sauvegarde une grille de reconstructions et une interpolation latente."""
    model.eval()
    images, _labels = next(iter(dataloader))
    images = images.to(device)[:8]
    with torch.no_grad():
        reconstruction, mu, _logvar = model(images)

    output_dir = Path(output_dir)
    reconstruction_path = save_image_grid(
        torch.cat([images.cpu(), reconstruction.cpu()]), output_dir / "vae_reconstructions.png"
    )
    interpolation_path = save_image_grid(
        interpolate(model, mu[0], mu[-1], steps=8), output_dir / "vae_interpolation.png"
    )
    return {
        "reconstructions": reconstruction_path,
        "interpolation": interpolation_path,
    }


@torch.no_grad()
def save_dcgan_samples(
    generator: DCGANGenerator, output_dir: Path, device: str = "cpu", seed: int = 42
) -> Path:
    generator.eval()
    generator.to(device)
    torch.manual_seed(seed)
    noise = torch.randn(16, generator.latent_dim, device=device)
    samples = (generator(noise) + 1) / 2
    return save_image_grid(samples, Path(output_dir) / "dcgan_samples.png", nrow=4)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Laboratoire VAE / DCGAN Fashion-MNIST")
    parser.add_argument("--model", choices=["vae", "dcgan"], default="vae")
    parser.add_argument("--epochs", type=int, default=1)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--limit-batches", type=int, default=None)
    parser.add_argument("--latent-dim", type=int, default=16)
    parser.add_argument("--lr", type=float, default=None)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--device", default="auto")
    parser.add_argument("--data-dir", type=Path, default=Path("data/fashion_mnist"))
    parser.add_argument("--output-dir", type=Path, default=Path("data/lab"))
    args = parser.parse_args(argv)

    device = resolve_device(args.device)
    loader = make_fashion_mnist_loader(args.data_dir, args.batch_size)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    if args.model == "vae":
        model = VAE(latent_dim=args.latent_dim)
        history = train_vae(
            model,
            loader,
            epochs=args.epochs,
            lr=args.lr or 1e-3,
            device=device,
            limit_batches=args.limit_batches,
            seed=args.seed,
            checkpoint_path=args.output_dir / "vae.pt",
        )
        samples = save_vae_samples(model, loader, args.output_dir, device)
    else:
        generator = DCGANGenerator(latent_dim=args.latent_dim)
        discriminator = DCGANDiscriminator()
        history = train_dcgan(
            generator,
            discriminator,
            loader,
            epochs=args.epochs,
            lr=args.lr or 2e-4,
            device=device,
            limit_batches=args.limit_batches,
            seed=args.seed,
            checkpoint_path=args.output_dir / "dcgan.pt",
        )
        samples = {"samples": save_dcgan_samples(generator, args.output_dir, device, args.seed)}

    (args.output_dir / f"{args.model}_history.json").write_text(
        json.dumps(history, indent=2), encoding="utf-8"
    )
    print(f"Modèle {args.model} entraîné sur {device}.")
    print("Dernière perte :", {key: values[-1] for key, values in history.items()})
    for name, path in samples.items():
        print(f"{name}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
