India Runs Data & AI Challenge

This repo contains the final submission pipeline, demo assets, and reproduction steps.

## Final submission
- Use `submission_final.csv` as the file to upload.
- It already follows the challenge validator format and rank ordering.

## Quick start
1. Create a virtual environment and install dependencies:

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

2. Regenerate the baseline and final files:

```bash
python score_candidates.py
python train_model.py
python ensemble_and_package.py
python hp_tune_and_ensemble.py
```

## Demo
- Open `demo.html` in a browser.
- It reads `top20.json` and shows the top candidates.

## What to submit
- `submission_final.csv`
- `submission_final_package.zip` or `submission_package.zip` if the portal asks for a ZIP
- GitHub repo link: `https://github.com/Ayeshasiddiqa789/india-runs-hackathon`

## Recommended repo contents
Keep:
- `score_candidates.py`
- `train_model.py`
- `ensemble_and_package.py`
- `hp_tune_and_ensemble.py`
- `requirements.txt`
- `README.md`
- `demo.html`
- `top20.json`
- `presentation_outline.md`

Optional to keep:
- `tune_weights.py`
- `auto_weights.py`
- `validate_local.py`
- `README_FINAL.md`
- `demo_script.md`

## Validation
If you want to re-check the CSV locally, run the provided validator on the generated submission file.
