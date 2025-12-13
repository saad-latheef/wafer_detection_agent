import pandas as pd
import numpy as np

df = pd.read_pickle("LSWMD.pkl")

# Safely extract failure type
df['ftype'] = df['failureType'].apply(
    lambda x: x[0][0] if isinstance(x, list) and len(x) > 0 else None
)

# Pick a real defective wafer
wafer = df[df['ftype'] != 'none'].iloc[0]['waferMap']

# Save for inference
np.save("real_input/wafer.npy", wafer)

print("✅ Real wafer saved:", wafer.shape)
