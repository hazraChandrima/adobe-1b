# Docker Setup Guide - Adobe Hackathon Challenge 1B

This guide provides comprehensive instructions for building and running the Adobe Hackathon Challenge 1B solution using Docker.

## 📋 Prerequisites

- Docker installed on your system
- At least 8GB of free disk space (for PyTorch and dependencies)
- Stable internet connection for initial build

## 🏗️ Building the Docker Image

### First Time Build (15-20 minutes)
The initial build downloads PyTorch (~821MB) and other ML dependencies:

```bash
DOCKER_BUILDKIT=1 sudo docker build --platform linux/amd64 -t adobe-outline-extractor .
```

**Expected Build Time:**
- **First build**: 15-20 minutes (downloading PyTorch)
- **Subsequent builds**: 30-60 seconds (uses cached layers)

### Build Progress Indicators
During the build, you'll see:
- System dependencies installation (~1 minute)
- PyTorch download (~10-12 minutes) - This is the longest step
- Other ML libraries (~2-3 minutes)
- Final image assembly (~1 minute)

## 🚀 Running the Application

### Basic Usage
Run analysis on each collection using these commands:

**Collection 1 (Travel Planning):**
```bash
sudo docker run -v "$(pwd)":/app adobe-outline-extractor ./Collection_1/
```

**Collection 2 (Adobe Acrobat Learning):**
```bash
sudo docker run -v "$(pwd)":/app adobe-outline-extractor ./Collection_2/
```

**Collection 3 (Recipe Collection):**
```bash
sudo docker run -v "$(pwd)":/app adobe-outline-extractor ./Collection_3/
```

### Interactive Mode
For running multiple collections or debugging:

```bash
sudo docker run -it -v "$(pwd)":/app adobe-outline-extractor bash

# Inside the container:
python run_analysis.py ./Collection_1/
python run_analysis.py ./Collection_2/
python run_analysis.py ./Collection_3/
```

## 📁 Output Files

Each command generates a `challenge1b_output.json` file in the respective collection directory:
- `Collection_1/challenge1b_output.json`
- `Collection_2/challenge1b_output.json`
- `Collection_3/challenge1b_output.json`

## 🔧 Docker Management

### Check Built Images
```bash
sudo docker images | grep adobe-outline-extractor
```

### Remove Old Images (Free Up Space)
```bash
# Remove unused images
sudo docker image prune

# Remove specific image
sudo docker rmi adobe-outline-extractor
```

### Clean Up System
```bash
# Remove all unused containers, networks, images
sudo docker system prune -a
```

## 🐛 Troubleshooting

### Common Issues

**1. "Unable to find image" error:**
```bash
# Check if image exists
sudo docker images

# If missing, rebuild
DOCKER_BUILDKIT=1 sudo docker build --platform linux/amd64 -t adobe-outline-extractor .
```

**2. Volume mounting issues with spaces in path:**
```bash
# Always use quotes around $(pwd)
sudo docker run -v "$(pwd)":/app adobe-outline-extractor ./Collection_1/
```

**3. Permission errors:**
```bash
# Ensure you're using sudo consistently
sudo docker run -v "$(pwd)":/app adobe-outline-extractor ./Collection_1/
```

**4. Out of disk space:**
```bash
# Check Docker space usage
sudo docker system df

# Clean up unused data
sudo docker system prune -a
```

### Performance Issues

**Slow build times:**
- First build downloads 800MB+ of ML libraries - this is normal
- Subsequent builds should be under 1 minute
- Ensure stable internet connection for downloads

**High memory usage during build:**
- Docker may use 4-6GB RAM during PyTorch installation
- Close other applications if system becomes unresponsive

## 📊 Resource Requirements

### Disk Space
- **Docker image**: ~6GB (includes PyTorch, transformers, etc.)
- **Build cache**: ~2-3GB additional
- **Total recommended**: 10GB free space

### Memory
- **Build time**: 4-6GB RAM recommended
- **Runtime**: 2-4GB RAM per container

### Network
- **Initial download**: ~1GB of Python packages
- **Subsequent builds**: Minimal network usage

## 🔄 Development Workflow

### Making Code Changes
1. Edit your Python files (run_analysis.py, etc.)
2. Rebuild the image:
   ```bash
   DOCKER_BUILDKIT=1 sudo docker build --platform linux/amd64 -t adobe-outline-extractor .
   ```
3. Build time: ~30-60 seconds (cached layers)

### Adding New Dependencies
1. Update `requirements.txt`
2. Rebuild the image (will re-download dependencies)
3. Build time: ~8-12 minutes

## 📋 Docker Files Overview

### Dockerfile Features
- **Multi-layer caching**: Optimized for fast rebuilds
- **BuildKit support**: Enhanced build performance
- **Pip caching**: Faster dependency installation
- **Minimal runtime**: Clean final image
- **ENTRYPOINT design**: Easy command-line usage

### .dockerignore Benefits
- Excludes virtual environments and cache files
- Reduces build context size
- Faster Docker builds
- Smaller final image

## ✅ Verification

### Test the Installation
```bash
# Quick test - should show Python version
sudo docker run adobe-outline-extractor python --version

# Full test - run on Collection 1
sudo docker run -v "$(pwd)":/app adobe-outline-extractor ./Collection_1/
```

### Expected Output
- Processing messages for document analysis
- Generated `Collection_1/challenge1b_output.json`
- No error messages

---

**Note**: The first Docker build takes 15-20 minutes due to PyTorch download. This is a one-time setup cost - subsequent builds are much faster!
