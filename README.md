# 🎯 Fast Splatting Gaussian Splatting (FSGS)

This repository contains an efficient pipeline for confidence-aware Gaussian Splatting with COLMAP-compatible outputs. It includes pose estimation, polygonal preprocessing, and point cloud generation for custom RGB image datasets.

---

## 📦 Setup Instructions (Windows + CUDA 12.6)

### ✅ Prerequisites

Ensure the following are installed:

- [Visual Studio 2022](https://visualstudio.microsoft.com/) (with Desktop C++ development tools)
- [CUDA Toolkit 12.6](https://developer.nvidia.com/cuda-downloads)
- [Miniconda or Anaconda](https://www.anaconda.com/)
- [Git](https://git-scm.com/)
- [COLMAP](https://github.com/colmap/colmap)

---

### 🔧 COLMAP Installation

#### Prebuilt Binary (Recommended)

1. Download the latest release from [COLMAP Releases](https://github.com/colmap/colmap/releases).
2. Extract it and add the directory to your system `PATH`.
3. Verify installation:

```bash
colmap -h
```
####  1. Clone with Submodules

```bash
git clone --recursive https://github.com/your_username/fsgs.git
cd fsgs
```
2. (Optional) Configure Environment Variables for CMake

```bash
set CUDA_TOOLKIT_ROOT_DIR="C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v12.6"
set CMAKE_MAKE_PROGRAM=msbuild
set CMAKE_GENERATOR="Visual Studio 17 2022"
```

Configure:

```bash
cmake -G "Visual Studio 17 2022" .
```

🐍 Python Environment
3. Create & Activate Environment

```bash
conda create -n fsgs python=3.8.1 -y
conda activate fsgs
```

4. Install PyTorch (CUDA 12.4 compatible)

```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
```
Verify:
```bash
python -c "import torch; print(torch.__version__); print(torch.cuda.is_available())"
```

5. Install Dependencies

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


## 🧑‍💻 Running the Pipeline

### 1. Organize Your Dataset

Your dataset should be structured like this:
```bash
your_dataset/
      ├── images/
```

### 2. To generate output cameras.txt image.txt and Point3D.txt
Run this command to generate polygonal masks if required for your dataset:
```bash
python tools/manual/polymap.py
```
You'll be prompted to enter the following paths:
path::  C:\path\to\your_dataset
path::  images

If it stop for fetures matching step, open colmap gui and then do it manually and come back again to this step afte feture matching.

### 3. Estimate Camera Poses
Run this script to estimate the camera poses and generate cameras.txt and images.txt files:

```bash
python tools/bounds/imgs2poses.py C:\path\to\your_dataset
```
Replace C:\path\to\your_dataset with the full path to your dataset.

### 4. Generate 3D Points
Run this final step to generate the fused point cloud .ply:

```bash
python tools/own.py
```
You'll be prompted to enter the following paths:
path::  C:\path\to\your_dataset\
Name::  your_scene_name
Views:: number of images for dense reconstruction

### Output Files
After running the pipeline, your dataset folder will contain the following files:
```bash
your_dataset/
    ├── images/
    ├── sparse/0/
        ├── cameras.txt        # From tools/manual/polymap.py
        ├── images.txt         # From tools/manual/polymap.py
        ├── points3D.txt       # From tools/manual/polymap.py
    ├── n_Views/dense
        ├── fused.ply          # From tools/own.py
    ├── poses_bounds.npy       # From tools/bounds/imgs2bounds.py
```
