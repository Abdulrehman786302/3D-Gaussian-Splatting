
# 🌐 Fast Splatting Gaussian Splatting (FSGS)

This repository contains code for fast and confidence-aware Gaussian Splatting using PyTorch and CUDA. It is designed for efficient 3D rendering and scene capture pipelines.

---

## 📦 Setup Instructions (Windows + CUDA 12.6)

### ✅ Prerequisites

Before proceeding, make sure the following software is installed:

- [Visual Studio 2022](https://visualstudio.microsoft.com/) (with C++ Desktop Development tools)
- [CUDA Toolkit 12.6](https://developer.nvidia.com/cuda-downloads)
- [Miniconda or Anaconda](https://www.anaconda.com/)
- `git` (to clone submodules)

---

### 🔧 Environment Setup

#### 1. Clone the repository

```bash
git clone --recursive https://github.com/VITA-Group/FSGS.git
cd fsgs
```
###  2. (Optional) Set Environment Variables
If needed, set these before building with CMake:

```bash
set CUDA_TOOLKIT_ROOT_DIR="C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v12.6"
set CMAKE_MAKE_PROGRAM=msbuild
set CMAKE_GENERATOR="Visual Studio 17 2022"

echo %CMAKE_GENERATOR%
echo %CMAKE_MAKE_PROGRAM%
```

#### 3. Configure CMake
From the root directory of the repo:

```bash
cmake -G "Visual Studio 17 2022" .
```

#### 4. Create Conda Environment

```bash
conda create -n fsgs python=3.8.1 -y
conda activate fsgs
```

#### 5. Install PyTorch with CUDA Support
Install the PyTorch version compatible with CUDA 12.4:

```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
python -c "import torch; print(torch.__version__); print(torch.cuda.is_available())"
```

#### 6. Python Dependencies

```bash
pip install setuptools==69.5.1
pip install submodules/diff-gaussian-rasterization-confidence/
pip install submodules/simple-knn/
pip install matplotlib==3.5.3
pip install torchmetrics==1.2.0
pip install timm==0.9.12
pip install opencv_python==4.8.1.78
pip install imageio==2.31.2
pip install open3d==0.17.0
pip install plyfile
```
## 🧭 Generate COLMAP-Compatible Output for Custom Datasets

This project supports generating `cameras.txt`, `images.txt`, and `points3D.txt` compatible with COLMAP from a custom image dataset.

### ✅ Input Requirements

- Image directory (`images/`)
- Features matching and Feature Extraction (used by `polymap.py`)
- Intrinsics and extrinsics estimation (via `imgs2poses.py`)
- Postprocessing and point fusion (via `own.py`)

---

## 🔧 Install COLMAP (Windows)

Before generating COLMAP-compatible files, install COLMAP.

### Option 1: Download Precompiled Binary (Recommended)

1. Go to the [COLMAP Releases](https://github.com/colmap/colmap/releases) page.
2. Download the latest **Windows .zip** build.
3. Extract and add the `COLMAP` directory to your system `PATH`.

To verify installation:

```bash
colmap -h
pip install enlighten
pip install pycolmap
```


### 📸 Step-by-Step Instructions

#### 1. Fecture extraction and Feacture matching dataset:

```bash
python tools/manual/polymap.py
```
Prompts:
path::  secne path
path::  images folder path

if it's stop in matching fectures process open colmap


### 2. Estimate Poses and Camera Parameters
This script creates COLMAP-style cameras.txt and images.txt files:

```bash
python tools/bounds/imgs2poses.py secence_path
```
Replace "secence_path" with the full path to your dataset root. Ensure it contains an images/ subfolder.


### 3. Generate 3D Points and Final fused.ply or dense reconstruction
This script generates the final COLMAP-compatible points3D.txt file:

```bash
python tools/own.py
```
Prompts:
path::  dataset path e.g FSGS\dataset
path::  secene name e.g \flame
views:: Number of view to use for dense reconstrctuion

📂 Output Structure
After running all steps, you should get:

```bash
dataset_root/
├── images/
├── sparse/0/
    ├── cameras.txt       # From polymap.py
    ├── images.txt        # From polymap.py
    ├── points3D.txt      
├── views/dense/          # From own.py
    ├── fused.ply         # point cloud
├── posess_bounds.npy     # From imgs2posess.py
```

