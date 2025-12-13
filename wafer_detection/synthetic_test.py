import numpy as np

# 0 = outside wafer
# 1 = normal die
# 2 = defective die

def center_defect(size=56):
    w = np.ones((size, size), dtype=int)
    c = size // 2
    w[c-5:c+5, c-5:c+5] = 2
    return w

def edge_ring_defect(size=56):
    w = np.ones((size, size), dtype=int)
    w[:5, :] = 2
    w[-5:, :] = 2
    w[:, :5] = 2
    w[:, -5:] = 2
    return w

def random_defect(size=56, p=0.1):
    w = np.ones((size, size), dtype=int)
    mask = np.random.rand(size, size) < p
    w[mask] = 2
    return w
