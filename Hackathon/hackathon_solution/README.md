Hackathon solution — India Runs Data & AI Challenge

This folder contains a Python baseline pipeline to generate a valid `submission.csv` for the challenge.

Quick start

1. Create a virtual environment and install dependencies:

```bash
python -m venv .venv
.venv\\Scripts\\activate    # Windows
pip install -r requirements.txt
```

2. Run the scorer (it reads the original dataset and writes `submission.csv`):

```bash
python score_candidates.py
```

Output: `submission.csv` in this folder. Then validate with the provided validator.
