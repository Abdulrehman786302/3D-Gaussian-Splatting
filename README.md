# 3D-Gaussian-Splatting
🚀 Installation Guide (Windows + CUDA 12.6)
1. Prerequisites

Ensure the following are installed:
Visual Studio 2022 with C++ components
CUDA Toolkit 12.6
Anaconda
2. Environment Setup:: Set environment variables (adjust path if needed):

set CUDA_TOOLKIT_ROOT_DIR="C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v12.6"
set CMAKE_MAKE_PROGRAM=msbuild
set CMAKE_GENERATOR="Visual Studio 17 2022"

:: Verify

echo %CMAKE_GENERATOR%
echo %CMAKE_MAKE_PROGRAM%
