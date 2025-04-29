
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




