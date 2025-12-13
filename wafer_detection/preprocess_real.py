import numpy as np
import torch
from PIL import Image

def preprocess_real_wafer(path):
    wafer = np.load(path)  # (H, W), values {0,1,2}

    h, w = wafer.shape
    rgb = np.zeros((h, w, 3), dtype=np.uint8)

    # one-hot encoding
    rgb[wafer == 0, 0] = 255  # non-wafer → R
    rgb[wafer == 1, 1] = 255  # normal → G
    rgb[wafer == 2, 2] = 255  # defect → B

    # resize to 56x56
    img = Image.fromarray(rgb).resize((56, 56))
    img = np.array(img).astype(np.float32) / 255.0

    # to tensor
    tensor = torch.from_numpy(img).permute(2, 0, 1).unsqueeze(0)

    return tensor
