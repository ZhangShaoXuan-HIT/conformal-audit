import numpy as np
import sklearn.tree._tree as t
if not hasattr(t, "DOUBLE"):
    t.DOUBLE = np.float64
if not hasattr(t, "DTYPE"):
    t.DTYPE = np.float32
try:
    import coverforest
    print("coverforest ok")
except Exception as e:
    print("ERR", type(e).__name__, e)
