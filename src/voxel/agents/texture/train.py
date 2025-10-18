"""
Texture Agent Trainer
- Trains a conditional diffusion UNet to output PBR maps given a text prompt.
- Expected dataset structure: data/texture/{split}/{id}/albedo.png, normal.png, rough.png, metal.png and a metadata.json with {"prompt": "..."}
- Based on HuggingFace diffusers minimal fine-tune loop.
- Credits: Step1X-3D (Apache-2.0), TEXTure (MIT) inspirations. Check their LICENSE files.
"""

import argparse
from pathlib import Path
from PIL import Image
import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import CLIPTokenizerFast, CLIPTextModel
from diffusers import UNet2DModel, DDPMScheduler, AutoencoderKL
from torchvision.transforms import ToTensor, Resize, Compose, Normalize

class PBRDataset(Dataset):
    def __init__(self, root:Path, size=256):
        self.root = Path(root)
        self.items = sorted([p for p in root.iterdir() if p.is_dir()])
        self.transform = Compose([Resize((size,size)), ToTensor()])
    def __len__(self): return len(self.items)
    def __getitem__(self, idx):
        p = self.items[idx]
        meta = (p/"metadata.json")
        if not meta.exists():
            prompt = "unknown material"
        else:
            import json
            prompt = json.loads(meta.read_text())["prompt"]
        # load maps
        albedo = Image.open(p/"albedo.png").convert("RGB")
        normal = Image.open(p/"normal.png").convert("RGB")
        rough = Image.open(p/"roughness.png").convert("L")
        metal = Image.open(p/"metallic.png").convert("L")
        albedo = self.transform(albedo)
        normal = self.transform(normal)
        rough = Resize((albedo.shape[1], albedo.shape[2]))(rough)
        rough = ToTensor()(rough)
        metal = Resize((albedo.shape[1], albedo.shape[2]))(metal)
        metal = ToTensor()(metal)
        # concat into tensor channels: RGB albedo, RGB normal, L rough, L metal => 8 channels
        maps = torch.cat([albedo, normal, rough, metal], dim=0)
        return {"maps": maps, "prompt": prompt}

def collate_fn(batch):
    prompts = [b["prompt"] for b in batch]
    maps = torch.stack([b["maps"] for b in batch])
    return {"maps": maps, "prompts": prompts}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", required=True)
    parser.add_argument("--out-dir", default="checkpoints/texture_agent")
    parser.add_argument("--epochs", type=int, default=10)
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--img-size", type=int, default=256)
    args = parser.parse_args()

    # load tokenizer / text encoder (CLIP)
    tokenizer = CLIPTokenizerFast.from_pretrained("openai/clip-vit-base-patch32")
    text_encoder = CLIPTextModel.from_pretrained("openai/clip-vit-base-patch32")

    # small UNet for proof-of-concept (use bigger models for production)
    unet = UNet2DModel(
        sample_size=args.img_size,
        in_channels=8,   # 8 channel maps (albedo rgb + normal rgb + rough + metal)
        out_channels=8,
        layers_per_block=2,
        block_out_channels=(64, 128, 256),
    )

    scheduler = DDPMScheduler.from_pretrained("google/ddpm-celebahq-256")
    vae = AutoencoderKL.from_pretrained("google/ddpm-celebahq-256", subfolder=None, local_files_only=False)  # placeholder

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    unet.to(device); text_encoder.to(device)

    ds = PBRDataset(Path(args.data_dir), size=args.img_size)
    dl = DataLoader(ds, batch_size=args.batch_size, shuffle=True, collate_fn=collate_fn, num_workers=4)

    optimizer = torch.optim.AdamW(unet.parameters(), lr=2e-4)

    for epoch in range(args.epochs):
        unet.train()
        for step, batch in enumerate(dl):
            maps = batch["maps"].to(device)
            # encode text prompts
            enc = tokenizer(batch["prompts"], padding=True, truncation=True, return_tensors="pt").to(device)
            text_embeds = text_encoder(**enc).last_hidden_state
            # sample noise and time
            noise = torch.randn_like(maps)
            timesteps = torch.randint(0, scheduler.num_train_timesteps, (maps.shape[0],), device=device).long()
            noisy_maps = maps + noise  # placeholder for actual forward diffusion
            # forward
            preds = unet(noisy_maps, timesteps, encoder_hidden_states=text_embeds).sample
            loss = torch.nn.functional.mse_loss(preds, maps)
            optimizer.zero_grad(); loss.backward(); optimizer.step()

            if step % 50 == 0:
                print(f"Epoch {epoch} step {step} loss {loss.item():.4f}")

        torch.save(unet.state_dict(), f"{args.out_dir}/unet_epoch{epoch}.pt")
    print("Texture training finished. Models saved to", args.out_dir)

if __name__ == "__main__":
    main()
