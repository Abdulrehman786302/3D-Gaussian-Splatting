# 3D-Gaussian-Splatting
🚀 Installation Guide (Windows + CUDA 12.6)
1. Prerequisites
Ensure the following are installed:

Visual Studio 2022 with C++ components

CUDA Toolkit 12.6

Miniconda or Anaconda

2. Environment Setup
cmd
Copier
Modifier
:: Set environment variables (adjust path if needed)
set CUDA_TOOLKIT_ROOT_DIR="C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v12.6"
set CMAKE_MAKE_PROGRAM=msbuild
set CMAKE_GENERATOR="Visual Studio 17 2022"

:: Verify
echo %CMAKE_GENERATOR%
echo %CMAKE_MAKE_PROGRAM%
3. Configure CMake
cmd
Copier
Modifier
:: Run this in the root directory of the project
cmake -G "Visual Studio 17 2022" .
4. Create and activate Conda environment
bash
Copier
Modifier
conda create -n fsgs python=3.8.1 -y
conda activate fsgs
5. Install PyTorch (CUDA 12.4-compatible build)
bash
Copier
Modifier
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
Verify installation:

bash
Copier
Modifier
python -c "import torch; print(torch.__version__); print(torch.cuda.is_available())"
6. Install dependencies
bash
Copier
Modifier
pip install setuptools==69.5.1
pip install submodules/diff-gaussian-rasterization-confidence/
pip install submodules/simple-knn/
pip install matplotlib==3.5.3 torchmetrics==1.2.0 timm==0.9.12 opencv_python==4.8.1.78 imageio==2.31.2 open3d==0.17.0
pip install plyfile

