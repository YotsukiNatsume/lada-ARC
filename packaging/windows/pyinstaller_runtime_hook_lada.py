import os
import sys

base_path = sys._MEIPASS

paths = [
    base_path,
    os.path.join(base_path, "bin"),
]

intel_runtime_dir = os.path.join(base_path, "intel_runtime")
if os.path.isdir(intel_runtime_dir):
    paths.append(intel_runtime_dir)

os.environ["PATH"] = os.pathsep.join(paths)
os.environ["LADA_MODEL_WEIGHTS_DIR"] = os.path.join(base_path, "model_weights")
os.environ["LOCALE_DIR"] = os.path.join(base_path, "lada", "locale")
