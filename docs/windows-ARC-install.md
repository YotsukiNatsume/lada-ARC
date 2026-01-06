<h1 align="center">
  <img src="packaging/flatpak/share/io.github.ladaapp.lada.png" alt="Lada Icon" style="display: block; width: 64px; height: 64px;">
  <br>
  Lada (Intel® Arc™ GPUs)
</h1>

*Lada* is a tool designed to recover pixelated adult videos (JAV). This fork is specifically optimized for **Intel ARC GPUs** and **Intel Xe2 Graphics** (Lunar Lake series).

> [!IMPORTANT]
> **NVIDIA Users:** This branch is customized for Intel hardware using Pytorch.xpu ， If you are using an NVIDIA GPU, please visit the [Original Repository](https://github.com/ladaapp/lada) for the standard installation.
- **NVIDIA Testing Completed:** If you encounter any bugs, please report them to me for prompt resolution.

## Features
- **Recover Pixelated Videos**: Restore pixelated or mosaic scenes using AI models.
- **Hardware Acceleration**: Full support for Intel XPU (GPU) and Intel QuickSync (QSV) for high-speed encoding.
- **Watch/Export**: Real-time preview via GUI or efficient batch processing via CLI.

---

## Performance & Hardware Requirements
Restoration quality varies by scene. A GPU with at least 4-6GB VRAM is recommended for a smooth experience.

---

## Installation (Windows + Intel GPU/nvdaia)

Follow these steps in **PowerShell (Run as Administrator)**.

## 1. Install System Dependencies

### 1.1 Open a PowerShell as Administrator and install the following programs via winget
```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
winget install --id Git.Git -e --source winget
winget install --id Gyan.FFmpeg -e --source winget
winget install --id Python.Python.3.12 -e --source winget
```

### 1.2 Reopen the Command Line and Create the Environment         
####Subsequent operations do not require administrator privileges.
```powershell
py -V  # Verify Python 3.12 is installed
py -3.12 -m venv lada
.\lada\Scripts\Activate.ps1
```

> [!IMPORTANT]
> Ensure the virtual environment is activated before proceeding.
---

## 2. Install PyTorch XPU and Verify
```powershell
# Initialize pytorch.xpu
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/xpu
```
---
```powershell
py -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'XPU Detected: {torch.xpu.is_available()}')"
```
---

##  3. Clone the Project and Install
Install the optimized PyTorch stack for Intel GPUs:
```powershell
git clone -b test https://github.com/YotsukiNatsume/lada-ARC.git

cd lada-ARC

python.exe -m pip install --upgrade pip

pip install -e ".[xpu]"
```
---

### 4 Download AI Models
```powershell
Invoke-WebRequest 'https://huggingface.co/ladaapp/lada/resolve/main/lada_mosaic_detection_model_v4_accurate.pt?download=true' -OutFile ".\model_weights\lada_mosaic_detection_model_v4_accurate.pt"

Invoke-WebRequest 'https://huggingface.co/ladaapp/lada/resolve/main/lada_mosaic_detection_model_v4_fast.pt?download=true' -OutFile ".\model_weights\lada_mosaic_detection_model_v4_fast.pt"

Invoke-WebRequest 'https://huggingface.co/ladaapp/lada/resolve/main/lada_mosaic_detection_model_v2.pt?download=true' -OutFile ".\model_weights\lada_mosaic_detection_model_v2.pt"

Invoke-WebRequest 'https://huggingface.co/ladaapp/lada/resolve/main/lada_mosaic_restoration_model_generic_v1.2.pth?download=true' -OutFile ".\model_weights\lada_mosaic_restoration_model_generic_v1.2.pth"
```

## Usage

### Command Line Interface (CLI)

```powershell
lada-cli --input "your_video.mp4" --output "restored_video.mp4" --encoder "h264_qsv"
```


---

CLI Arguments Reference

| Argument | Description |
| :--- | :--- |
| `--input` | Path to the input video. |
| `--output` | Path to save the restored video. |
| `--device xpu` | Enable Arc™ GPUs acceleration (optional for Intel® users). |
| `--device cuda` | Enable NVIDIA GPU acceleration (optional for NVIDIA users). |
| `--device auto` | Automatically select device (xpu > cuda > cpu) if unspecified. |
| `--encoder "h264_qsv"` | Use hardware encoder (ignored if using presets). |
| `--list-devices` | Show available GPU devices. |
| `--encoding-preset h264-qsv-medium` | Use encoder presets. |
| `--list-encoding-presets` | Show all available encoder presets. |
| `--mosaic-detection-model` | Specify a custom model for detection. |
