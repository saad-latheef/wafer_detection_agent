import numpy as np
import torch
from PIL import Image

def wafer_to_tensor(wafer, device):
    h, w = wafer.shape
    rgb = np.zeros((h, w, 3), dtype=np.float32)

    for i in range(h):
        for j in range(w):
            rgb[i, j, int(wafer[i, j])] = 1

    img = Image.fromarray((rgb * 255).astype("uint8")).resize((56,56))
    img = np.array(img) / 255.0

    tensor = torch.tensor(img, dtype=torch.float32).permute(2,0,1).unsqueeze(0)

    return tensor.to(device)
