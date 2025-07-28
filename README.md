Here is the updated **`README.md`** without emojis:

```markdown
# Adobe Hackathon Challenge – Outline Extractor

This project extracts outlines from PDF collections using NLP and ML models.  
It is containerized with Docker for easy deployment.

---

## Project Structure
```

adobe-hackathon-challenge1b-master/
├── Collection\_1/                # Input PDF files for collection 1
├── Collection\_2/                # Input PDF files for collection 2
├── Collection\_3/                # Input PDF files for collection 3
├── Scripts/                     # Helper scripts and utilities
│   ├── dumppdf.py
│   ├── pdf2txt.py
│   └── ...
├── venv/                        # Local virtual environment (excluded in Docker)
├── Dockerfile                   # Docker build file
├── requirements.txt             # Python dependencies
├── run\_analysis.py              # Main script to process collections
├── approach\_explanation.md      # Approach explanation
└── README.md                    # Project documentation

````

---

## Prerequisites
- Docker installed on your system
- Ensure the input PDF files are placed inside `Collection_1`, `Collection_2`, or `Collection_3`

---

## How to Build and Run

### 1. Build the Docker image
```bash
docker build -t adobe-challenge .
````

---

### 2. Run the container for Collection 1

```bash
docker run --rm \
  -v "$PWD/Collection_1:/app/Collection_1" \
  adobe-challenge \
  python run_analysis.py ./Collection_1/
```

---

### 3. Run for Collection 2

```bash
docker run --rm \
  -v "$PWD/Collection_2:/app/Collection_2" \
  adobe-challenge \
  python run_analysis.py ./Collection_2/
```

---

### 4. Run for Collection 3

```bash
docker run --rm \
  -v "$PWD/Collection_3:/app/Collection_3" \
  adobe-challenge \
  python run_analysis.py ./Collection_3/
```

---

## Notes

* The `-v` flag mounts the host folder (e.g., `Collection_1`) into the container for processing.
* Replace `Collection_X` with the appropriate folder name to process different collections.
* The script `run_analysis.py` will handle the extraction and generate results.

---

## Troubleshooting

* If the build is slow, ensure `.dockerignore` is used to exclude unnecessary files (like `venv/`, `__pycache__/`, etc.).
* For faster builds, avoid installing GPU packages if not required.

---
```
```

