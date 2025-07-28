# Adobe Hackathon Challenge 1B - Docker Setup

A Dockerized solution for persona-driven document intelligence using advanced RAG (Retrieval-Augmented Generation) pipeline.

## 📁 Project Structure

```
adobe-hackathon-challenge1b-master/
├── Collection_1/                  # Travel Planning documents
├── Collection_2/                  # Adobe Acrobat Learning documents  
├── Collection_3/                  # Recipe Collection documents
├── Scripts/                       # Python executables and cache
├── venv/                         # Virtual environment (excluded from Docker)
├── .dockerignore                 # Docker build exclusions
├── .gitignore                    # Git exclusions
├── Dockerfile                    # Docker build configuration
├── README.md                     # This file
├── requirements.txt              # Python dependencies
└── run_analysis.py              # Main analysis script
```

## 🚀 Quick Start

### 1. Build the Docker Image

```bash
docker build -t adobe-challenge .
```

**Expected Build Time:**
- **First build**: 25-35 minutes (downloads PyTorch + CUDA libraries ~1.5GB)
- **Subsequent builds**: 30-60 seconds (uses cached layers)

### 2. Run Analysis on Collections

**Collection 1 (Travel Planning):**
```bash
docker run --rm \
  -v "$PWD/Collection_1:/app/Collection_1" \
  adobe-challenge \
  python run_analysis.py ./Collection_1/
```

**Collection 2 (Adobe Acrobat Learning):**
```bash
docker run --rm \
  -v "$PWD/Collection_2:/app/Collection_2" \
  adobe-challenge \
  python run_analysis.py ./Collection_2/
```

**Collection 3 (Recipe Collection):**
```bash
docker run --rm \
  -v "$PWD/Collection_3:/app/Collection_3" \
  adobe-challenge \
  python run_analysis.py ./Collection_3/
```

## 📋 Prerequisites

- **Docker**: Latest version installed
- **System Requirements**:
  - 10GB+ free disk space (for ML models and dependencies)
  - 8GB+ RAM (4GB minimum)
  - Stable internet connection for initial build

## 🔧 Advanced Usage

### Interactive Mode
For debugging or running multiple collections:

```bash
docker run --rm -it \
  -v "$PWD:/app" \
  adobe-challenge bash

# Inside container:
python run_analysis.py ./Collection_1/
python run_analysis.py ./Collection_2/
python run_analysis.py ./Collection_3/
```

### Mount All Collections at Once
```bash
docker run --rm \
  -v "$PWD:/app" \
  adobe-challenge \
  python run_analysis.py ./Collection_1/
```

## 📁 Output Files

Each analysis generates a JSON output file in the respective collection:
- `Collection_1/challenge1b_output.json`
- `Collection_2/challenge1b_output.json`
- `Collection_3/challenge1b_output.json`

## 🏗️ Build Process Details

### What Gets Downloaded During Build:
1. **Base Python image** (~100MB)
2. **System dependencies** (build tools, gcc)
3. **PyTorch** (~821MB) - Deep learning framework
4. **CUDA libraries** (~600MB) - GPU acceleration support
5. **Transformers & ML libraries** (~300MB)
6. **Other dependencies** (~200MB)

**Total download**: ~1.5-2GB

### Build Stages:
```
[1/6] Base image setup               (~1 min)
[2/6] System dependencies            (~2 min)  
[3/6] Python requirements install    (~25-30 min)
  ├── PyTorch download               (~10-15 min)
  ├── CUDA libraries download        (~8-12 min)
  └── Other ML libraries             (~5-8 min)
[4/6] Copy application code          (~10 sec)
[5/6] Cleanup & optimization         (~30 sec)
[6/6] Final image assembly           (~10 sec)
```

## 🐛 Troubleshooting

### Build Issues

**Slow build times:**
```bash
# Use BuildKit for better performance
DOCKER_BUILDKIT=1 docker build -t adobe-challenge .

# Check available disk space
docker system df
```

**Out of memory during build:**
```bash
# Close other applications
# Increase Docker memory limit in Docker Desktop
# Or build with limited parallelism:
docker build --memory=4g -t adobe-challenge .
```

### Runtime Issues

**Permission errors:**
```bash
# Ensure proper volume mounting
docker run --rm -v "$PWD/Collection_1:/app/Collection_1" adobe-challenge python run_analysis.py ./Collection_1/
```

**Path issues with spaces:**
```bash
# Use quotes around paths
docker run --rm -v "$PWD/Collection_1:/app/Collection_1" adobe-challenge python run_analysis.py ./Collection_1/
```

**Container not found:**
```bash
# Check if image exists
docker images | grep adobe-challenge

# Rebuild if missing
docker build -t adobe-challenge .
```

## 🔍 Verification

### Check Build Success
```bash
# List built images
docker images adobe-challenge

# Test Python installation
docker run --rm adobe-challenge python --version

# Test dependencies
docker run --rm adobe-challenge python -c "import torch; print(f'PyTorch: {torch.__version__}')"
```

### Validate Analysis
```bash
# Run on Collection_1 and check output
docker run --rm -v "$PWD/Collection_1:/app/Collection_1" adobe-challenge python run_analysis.py ./Collection_1/

# Verify output file exists
ls -la Collection_1/challenge1b_output.json
```

## 🧹 Cleanup

### Remove Built Images
```bash
# Remove specific image
docker rmi adobe-challenge

# Remove all unused images
docker image prune -a
```

### Clean Build Cache
```bash
# Remove build cache
docker builder prune

# Complete cleanup (removes everything)
docker system prune -a --volumes
```

## ⚡ Performance Tips

1. **First build optimization**:
   - Ensure stable internet connection
   - Close memory-heavy applications
   - Use SSD storage if available

2. **Development workflow**:
   - Keep the built image - rebuilds are fast
   - Use interactive mode for testing
   - Mount specific collections for targeted analysis

3. **Resource monitoring**:
   ```bash
   # Monitor container resources
   docker stats
   
   # Check disk usage
   docker system df
   ```

## 🔬 Technical Details

### Docker Features Used:
- **Multi-stage build**: Optimized image size
- **BuildKit**: Enhanced build performance  
- **Volume mounting**: Access to host collections
- **Automatic cleanup**: `--rm` flag removes containers after use

### AI Models Loaded:
- **Semantic search**: sentence-transformers model
- **Title generation**: google/flan-t5-base
- **Document processing**: PyTorch-based pipeline

## 📊 Expected Performance

| Operation | Time | Notes |
|-----------|------|-------|
| First build | 25-35 min | Downloads 1.5GB+ dependencies |
| Rebuild (code changes) | 30-60 sec | Uses cached layers |
| Collection_1 analysis | 2-5 min | Depends on document count |
| Collection_2 analysis | 2-5 min | Depends on document count |  
| Collection_3 analysis | 2-5 min | Depends on document count |

## 🆘 Support

### Common Error Messages:

**"No space left on device"**
```bash
docker system prune -a
df -h  # Check disk space
```

**"Error response from daemon: pull access denied"**
```bash
# Check image name spelling
docker images
docker build -t adobe-challenge .
```

- This is normal - models are loading into memory
- Wait 1-2 minutes for initialization

---

