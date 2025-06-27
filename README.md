# COLMAP API

A REST API for Structure from Motion (SfM) reconstruction using [Hierarchical Localization (hloc)](https://github.com/cvg/Hierarchical-Localization) and COLMAP. This API provides an easy-to-use endpoint for generating 3D reconstructions from a set of images.

## Overview

This project wraps the powerful hloc toolbox in a simple FastAPI interface, allowing you to perform SfM reconstruction through HTTP requests. The API handles the complete pipeline from feature extraction to 3D reconstruction, returning a downloadable zip file containing the COLMAP model.

## Features

- **REST API**: Simple HTTP interface for SfM reconstruction
- **Configurable Pipeline**: Support for different feature extractors, matchers, and retrieval methods
- **Multiple Algorithms**: 
  - Feature extractors: SuperPoint, DISK, SIFT, R2D2, etc.
  - Feature matchers: SuperGlue, LightGlue, nearest neighbor matching
  - Image retrieval: NetVLAD, DenseVLAD, etc.
- **Docker Support**: Containerized deployment with GPU support
- **Automatic Processing**: Handles the complete SfM pipeline automatically

## API Endpoint

### POST `/sfm`

Performs Structure from Motion reconstruction on uploaded images.

**Parameters:**
- `images`: List of image files to process (required)
- `retrieval_conf_key`: Configuration for image retrieval (default: "netvlad")
- `feature_conf_key`: Configuration for feature extraction (default: "superpoint_aachen")
- `matcher_conf_key`: Configuration for feature matching (default: "superpoint+lightglue")

**Returns:**
- Success: ZIP file containing the COLMAP reconstruction model
- Error: JSON response with error details

**Example using curl:**
```bash
curl -X POST "http://localhost:8000/sfm" \
  -F "images=@image1.jpg" \
  -F "images=@image2.jpg" \
  -F "images=@image3.jpg" \
  -F "retrieval_conf_key=netvlad" \
  -F "feature_conf_key=superpoint_aachen" \
  -F "matcher_conf_key=superpoint+lightglue" \
  --output sfm_result.zip
```

## Installation & Usage

### Using Docker (Recommended)

#### Build the Docker image:
```bash
docker build -t colmap-api:latest .
```

#### Or pull the pre-built image from Docker Hub:
```bash
docker pull jourdelune876/colmap-api:latest
docker tag jourdelune876/colmap-api:latest colmap:latest
```

#### Run the container:
```bash
# CPU only
docker run --ipc=host -p 8000:8000 colmap-api:latest

# With GPU support (requires nvidia-docker)
docker run --gpus all --ipc=host -p 8000:8000 colmap:latest
```

The API will be available at `http://localhost:8000` and the docs at `http://localhost:8000/docs`.

### Local Installation

1. Clone the repository:
```bash
git clone --recursive https://github.com/yourusername/colmap-api.git
cd colmap-api
```

2. Install dependencies:
```bash
pip install ./Hierarchical-Localization
pip install .
```

3. Run the API:
```bash
export PYTHONPATH="./Hierarchical-Localization:$PYTHONPATH"
fastapi run api.py
```

## Configuration Options

The API supports various pre-configured feature extractors and matchers from hloc:

### Feature Extractors (`feature_conf_key`):
- `superpoint_aachen`: SuperPoint optimized for outdoor scenes
- `superpoint_max`: SuperPoint with maximum keypoints
- `disk`: DISK feature detector and descriptor
- `sift`: Classical SIFT features
- `r2d2`: R2D2 features

### Feature Matchers (`matcher_conf_key`):
- `superpoint+lightglue`: SuperPoint with LightGlue matcher (fast)
- `superglue`: SuperGlue matcher (slower but more accurate)
- `NN-ratio`: Nearest neighbor matching with ratio test

### Image Retrieval (`retrieval_conf_key`):
- `netvlad`: NetVLAD global descriptors
- `densevlad`: DenseVLAD descriptors

## Example Usage with Python

```python
import requests

# Prepare images
files = [
    ('images', open('image1.jpg', 'rb')),
    ('images', open('image2.jpg', 'rb')),
    ('images', open('image3.jpg', 'rb'))
]

# Optional parameters
data = {
    'retrieval_conf_key': 'netvlad',
    'feature_conf_key': 'superpoint_aachen',
    'matcher_conf_key': 'superpoint+lightglue'
}

# Make request
response = requests.post('http://localhost:8000/sfm', files=files, data=data)

if response.status_code == 200:
    with open('reconstruction.zip', 'wb') as f:
        f.write(response.content)
    print("SfM reconstruction completed successfully!")
else:
    print(f"Error: {response.json()}")
```

## Output Format

The API returns a ZIP file containing the COLMAP reconstruction with the following structure:
```
sfm_output.zip
├── database.db          # COLMAP database
├── cameras.bin          # Camera parameters
├── images.bin           # Image poses and observations
├── points3D.bin         # 3D point cloud
└── models/              # Additional model files
```

## Technical Details

This API is built on top of:
- **[hloc](https://github.com/cvg/Hierarchical-Localization)**: Hierarchical localization toolbox
- **[COLMAP](https://colmap.github.io/)**: Structure-from-Motion software
- **[pycolmap](https://github.com/colmap/pycolmap)**: Python bindings for COLMAP
- **[FastAPI](https://fastapi.tiangolo.com/)**: Modern web framework for building APIs

## Requirements

- Python ≥ 3.7
- PyTorch ≥ 1.1
- CUDA (optional, for GPU acceleration)
- Docker (for containerized deployment)

## Limitations

- Input images should have sufficient overlap for successful reconstruction
- Very large image sets may require significant processing time and memory
- GPU acceleration is recommended for better performance

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

## License

This project builds upon hloc and COLMAP. Please refer to their respective licenses:
- [hloc license](https://github.com/cvg/Hierarchical-Localization/blob/master/LICENSE)
- [COLMAP license](https://github.com/colmap/colmap/blob/dev/LICENSE.txt)

## Citation

If you use this API in your research, please cite the original hloc paper:

```bibtex
@inproceedings{sarlin2019coarse,
  title={From Coarse to Fine: Robust Hierarchical Localization at Large Scale},
  author={Sarlin, Paul-Edouard and Cadena, Cesar and Siegwart, Roland and Dymczyk, Marcin},
  booktitle={CVPR},
  year={2019}
}
```