import os
import sys

base_path = sys._MEIPASS

torch_lib_path = os.path.join(base_path, "torch", "lib")

os.environ["PATH"] = os.pathsep.join([
    torch_lib_path,
    base_path,
    os.path.join(base_path, "bin"),
    os.environ.get("PATH", "")
])

os.environ["LADA_MODEL_WEIGHTS_DIR"] = os.path.join(base_path, "model_weights")
os.environ["LOCALE_DIR"] = os.path.join(base_path, "lada", "locale")