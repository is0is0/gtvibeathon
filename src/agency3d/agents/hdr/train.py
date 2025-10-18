"""
HDR Agent Trainer
- Trains a conditional UNet to convert LDR panorama + prompt -> HDR equirectangular map
- Dataset assumed: data/hdr/{id}/ldr.png, hdr.exr (float), metadata.json with {"prompt":"..."}
- Credits / inspiration: single_image_hdr (MIT)
"""

import argparse
from pathlib import Path
import torch
from torch.utils.data import Dataset, DataLoader
from PIL import Image
import numpy as np
import OpenEXR, Imath   # optional: if not installed, use .npy float maps instead
from torchvision.transforms import Compose, Resize, ToTensor
from diffusers import UNet2DModel  # or simple UNet

class HDRDataset(Dataset):
    def __init__(self, root:Path, size=512):
        self.root = Path(root)
        self.items = sorted([p for p in root.iterdir() if p.is_dir()])
        self.transform = Compose([Resize((size, size)), ToTensor()])
    def __len__(self): return len(self.items)
    def __getitem__(self, idx):
        p = self.items[idx]
        ldr = Image.open(p/"ldr.png").convert("RGB")
        ldr = self.transform(ldr)
        # load hdr as numpy float (e.g., .npy or use OpenEXR)
        hdr_path = p/"hdr.npy"
        if hdr_path.exists():
            hdr = torch.from_numpy(np.load(hdr_path)).permute(2,0,1)
        else:
            # fallback: load LDR and upscale (training will be weak)
            hdr = ldr.clone()
        prompt = "unknown"
        meta = p/"metadata.json"
        if meta.exists():
            import json
            prompt = json.loads(meta.read_text()).get("prompt","unknown")
        return {"ldr": ldr, "hdr": hdr, "prompt": prompt}

def collate_fn(batch):
    ldr = torch.stack([b["ldr"] for b in batch])
    hdr = torch.stack([b["hdr"] for b in batch])
    prompts = [b["prompt"] for b in batch]
    return {"ldr": ldr, "hdr": hdr, "prompts": prompts}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", required=True)
    parser.add_argument("--out-dir", default="checkpoints/hdr_agent")
    parser.add_argument("--epochs", type=int, default=10)
    parser.add_argument("--batch-size", type=int, default=2)
    parser.add_argument("--img-size", type=int, default=512)
    args = parser.parse_args()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    # Simple UNet model
    unet = UNet2DModel(sample_size=args.img_size, in_channels=3, out_channels=3, block_out_channels=(64,128,256))
    unet.to(device)

    ds = HDRDataset(Path(args.data_dir), size=args.img_size)
    dl = DataLoader(ds, batch_size=args.batch_size, shuffle=True, collate_fn=collate_fn, num_workers=4)

    opt = torch.optim.AdamW(unet.parameters(), lr=2e-4)
    for epoch in range(args.epochs):
        unet.train()
        for i, batch in enumerate(dl):
            ldr = batch["ldr"].to(device)
            hdr = batch["hdr"].to(device)
            # simple forward
            pred = unet(ldr).sample  # diffusers UNet returns object; this is simplified
            loss = torch.nn.functional.mse_loss(pred, hdr)
            opt.zero_grad(); loss.backward(); opt.step()
            if i % 20 == 0:
                print(f"Epoch {epoch} step {i} loss {loss.item():.4f}")
        torch.save(unet.state_dict(), f"{args.out_dir}/unet_epoch{epoch}.pt")
    print("HDR training complete; outputs:", args.out_dir)

if __name__ == "__main__":
    main()
